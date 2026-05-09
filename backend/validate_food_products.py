"""
validate_food_products.py
─────────────────────────
Stand-alone script that validates FOOD PRODUCT labels against
Legal Metrology (Packaged Commodities) Rules, 2011.

Checks:
  1. MRP
  2. Manufacturer Name
  3. Net Quantity
  4. Manufacturing Date
  5. Expiry Date
  6. FSSAI License Number
  7. Customer Care Details
  8. Importer Details
  9. Country of Origin

Generates:
  - Compliance Status
  - Missing Fields
  - Risk Level
  - Compliance Score (0-100)
  - Structured JSON Report

Usage:
    python validate_food_products.py                  # validate all food products
    python validate_food_products.py --product "Tata Salt"  # validate a single product
"""

import csv
import json
import os
import sys
from datetime import datetime

# ─── Path setup ──────────────────────────────────────────────────────────────
DATASET_PATH = os.path.join(os.path.dirname(__file__), "data", "ecommerce_products_dataset.csv")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "data", "compliance_reports")


# ═══════════════════════════════════════════════════════════════════════════════
# Food Product Compliance Validator  (Legal Metrology Rules 2011)
# ═══════════════════════════════════════════════════════════════════════════════

class FoodProductValidator:
    """Validates food product labels against Legal Metrology Rules 2011."""

    # Mandatory fields for FOOD category (with rule references)
    FOOD_MANDATORY_FIELDS = {
        "mrp": {
            "display": "Maximum Retail Price (MRP)",
            "rule": "Rule 6(1)(f) — MRP inclusive of all taxes",
            "severity": "CRITICAL",
        },
        "manufacturer": {
            "display": "Manufacturer Name & Address",
            "rule": "Rule 6(1)(b) — Name and complete address of manufacturer/packer",
            "severity": "CRITICAL",
        },
        "net_quantity": {
            "display": "Net Quantity",
            "rule": "Rule 6(1)(c) — Net quantity by weight, measure, or number",
            "severity": "CRITICAL",
        },
        "manufacturing_date": {
            "display": "Manufacturing / Packing Date",
            "rule": "Rule 6(1)(d) — Month and year of manufacture or packing",
            "severity": "HIGH",
        },
        "expiry_date": {
            "display": "Expiry / Best Before Date",
            "rule": "Rule 6(1)(e) — Best before or use by date",
            "severity": "CRITICAL",
        },
        "fssai_license": {
            "display": "FSSAI License Number",
            "rule": "FSS Act 2006, Section 31 — FSSAI license mandatory for food products",
            "severity": "CRITICAL",
        },
        "customer_care": {
            "display": "Customer Care Details",
            "rule": "Rule 6(1)(h) — Consumer care contact details",
            "severity": "HIGH",
        },
        "importer": {
            "display": "Importer Name & Address",
            "rule": "Rule 6(1)(g) — Required for imported goods",
            "severity": "HIGH",
            "conditional": True,  # only required for imported products
        },
        "country_of_origin": {
            "display": "Country of Origin",
            "rule": "Rule 6(1)(g) — Country of origin for imported products",
            "severity": "HIGH",
        },
    }

    def validate_product(self, product_row: dict) -> dict:
        """
        Validate a single food product row from the dataset.

        Returns a structured compliance report dict.
        """
        product_name = product_row.get("product_name", "Unknown")
        is_imported = self._is_imported(product_row)

        # ── Field extraction ──────────────────────────────────────────
        fields = {
            "mrp":                product_row.get("mrp", "").strip(),
            "manufacturer":       product_row.get("manufacturer", "").strip(),
            "net_quantity":       product_row.get("net_quantity", product_row.get("quantity", "")).strip(),
            "manufacturing_date": product_row.get("manufacturing_date", "").strip(),
            "expiry_date":        product_row.get("expiry_date", product_row.get("expiry", "")).strip(),
            "fssai_license":      product_row.get("fssai_license", "").strip(),
            "customer_care":      product_row.get("customer_care", "").strip(),
            "importer":           product_row.get("importer", "").strip(),
            "country_of_origin":  product_row.get("country_of_origin", "").strip(),
        }

        # ── Validate each mandatory field ─────────────────────────────
        validation_results = []
        missing_fields = []
        violations = []

        for key, meta in self.FOOD_MANDATORY_FIELDS.items():
            value = fields.get(key, "")

            # Skip importer check for domestic products
            if meta.get("conditional") and not is_imported:
                validation_results.append({
                    "field": meta["display"],
                    "value": value or "N/A (Domestic product)",
                    "status": "NOT_APPLICABLE",
                    "rule": meta["rule"],
                })
                continue

            # Handle "N/A", "Unknown", or empty
            is_present = bool(value) and value.lower() not in ("n/a", "unknown", "")

            if is_present:
                validation_results.append({
                    "field": meta["display"],
                    "value": value,
                    "status": "VALID",
                    "rule": meta["rule"],
                })
            else:
                missing_fields.append(meta["display"])
                violations.append({
                    "field": meta["display"],
                    "description": f'{meta["display"]} is missing or invalid',
                    "severity": meta["severity"],
                    "rule_violated": meta["rule"],
                })
                validation_results.append({
                    "field": meta["display"],
                    "value": value or "—",
                    "status": "MISSING",
                    "rule": meta["rule"],
                })

        # ── Scoring ───────────────────────────────────────────────────
        applicable_fields = [
            v for v in validation_results if v["status"] != "NOT_APPLICABLE"
        ]
        total = len(applicable_fields)
        valid = sum(1 for v in applicable_fields if v["status"] == "VALID")
        score = round((valid / total) * 100, 2) if total > 0 else 0.0

        # ── Risk Level ────────────────────────────────────────────────
        critical_count = sum(1 for v in violations if v["severity"] == "CRITICAL")
        if score < 40 or critical_count >= 3:
            risk_level = "CRITICAL"
        elif score < 60 or critical_count >= 1:
            risk_level = "HIGH"
        elif score < 80:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        # ── Compliance Status ─────────────────────────────────────────
        if score == 100:
            status = "FULLY_COMPLIANT"
        elif score >= 70:
            status = "PARTIALLY_COMPLIANT"
        else:
            status = "NON_COMPLIANT"

        # ── Build Report ──────────────────────────────────────────────
        report = {
            "report_id": f"FOOD-RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{hash(product_name) % 10000:04d}",
            "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "legal_framework": "Legal Metrology (Packaged Commodities) Rules, 2011",

            "product_details": {
                "product_name": product_name,
                "category": product_row.get("category", "Food"),
                "is_imported": is_imported,
            },

            "label_fields": {
                "mrp": fields["mrp"] or None,
                "manufacturer": fields["manufacturer"] or None,
                "net_quantity": fields["net_quantity"] or None,
                "manufacturing_date": fields["manufacturing_date"] or None,
                "expiry_date": fields["expiry_date"] or None,
                "fssai_license": fields["fssai_license"] or None,
                "customer_care": fields["customer_care"] or None,
                "importer": fields["importer"] if is_imported else "N/A (Domestic)",
                "country_of_origin": fields["country_of_origin"] or None,
            },

            "validation_results": validation_results,
            "missing_fields": missing_fields,
            "violations": violations,

            "compliance_summary": {
                "compliance_score": score,
                "compliance_status": status,
                "risk_level": risk_level,
                "total_fields_checked": total,
                "valid_fields": valid,
                "missing_count": len(missing_fields),
                "violation_count": len(violations),
            },

            "remarks": self._generate_remarks(
                product_name, score, risk_level, status, missing_fields, violations
            ),

            "recommendations": self._generate_recommendations(
                missing_fields, violations, is_imported
            ),
        }

        return report

    # ── Helpers ────────────────────────────────────────────────────────────

    def _is_imported(self, row: dict) -> bool:
        """Check if the product is imported."""
        origin = row.get("country_of_origin", "").strip().lower()
        importer = row.get("importer", "").strip().lower()
        return (
            origin not in ("", "india", "n/a")
            or (importer not in ("", "n/a") and importer != "n/a (domestic)")
        )

    def _generate_remarks(
        self, name, score, risk, status, missing, violations
    ) -> str:
        parts = []

        if status == "FULLY_COMPLIANT":
            parts.append(
                f"✅ Product '{name}' is FULLY COMPLIANT with Legal Metrology "
                f"(Packaged Commodities) Rules, 2011. Score: {score}%."
            )
        elif status == "PARTIALLY_COMPLIANT":
            parts.append(
                f"⚠️ Product '{name}' is PARTIALLY COMPLIANT. Score: {score}%. "
                f"{len(missing)} mandatory field(s) are missing."
            )
        else:
            parts.append(
                f"❌ Product '{name}' is NON-COMPLIANT. Score: {score}%. "
                f"{len(missing)} mandatory field(s) missing. "
                f"Immediate corrective action required."
            )

        if risk in ("HIGH", "CRITICAL"):
            parts.append(
                f"🚨 RISK LEVEL: {risk}. This product may be subject to seizure "
                f"and penalties under Section 36 of the Legal Metrology Act, 2009."
            )

        if missing:
            parts.append(f"Missing: {', '.join(missing)}.")

        return " ".join(parts)

    def _generate_recommendations(self, missing, violations, is_imported) -> list:
        recs = []
        if missing:
            recs.append(
                f"Add the following mandatory fields to the label: {', '.join(missing)}"
            )
        if any(v["severity"] == "CRITICAL" for v in violations):
            recs.append(
                "URGENT: Resolve all CRITICAL violations before product distribution."
            )
        if is_imported and "Importer Name & Address" in missing:
            recs.append(
                "Imported products MUST display importer name and address "
                "per Rule 6(1)(g)."
            )

        # Standard recommendations
        recs.extend([
            "Ensure MRP is printed in Indian Rupees (₹) inclusive of all taxes.",
            "Net quantity must be in standard metric units (g, kg, ml, L).",
            "Manufacturing and expiry dates should use MM/YYYY or DD/MM/YYYY format.",
            "FSSAI license number is mandatory for all food products sold in India.",
            "Customer care number must be a working toll-free or landline number.",
        ])
        return recs


# ═══════════════════════════════════════════════════════════════════════════════
# CLI Runner
# ═══════════════════════════════════════════════════════════════════════════════

def load_dataset(path: str) -> list[dict]:
    """Load the CSV dataset."""
    products = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            products.append(row)
    return products


def print_report_summary(report: dict):
    """Pretty-print a compliance report to the console."""
    s = report["compliance_summary"]
    p = report["product_details"]

    # Header
    print("\n" + "═" * 70)
    print(f"  COMPLIANCE REPORT — {p['product_name']}")
    print("═" * 70)
    print(f"  Report ID      : {report['report_id']}")
    print(f"  Date           : {report['generated_date']}")
    print(f"  Category       : {p['category']}")
    print(f"  Imported       : {'Yes' if p['is_imported'] else 'No'}")
    print("─" * 70)

    # Compliance Summary
    status_icon = {"FULLY_COMPLIANT": "✅", "PARTIALLY_COMPLIANT": "⚠️", "NON_COMPLIANT": "❌"}
    risk_icon = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🟠", "CRITICAL": "🔴"}

    print(f"  Status         : {status_icon.get(s['compliance_status'], '')} {s['compliance_status']}")
    print(f"  Score          : {s['compliance_score']}%")
    print(f"  Risk Level     : {risk_icon.get(s['risk_level'], '')} {s['risk_level']}")
    print(f"  Fields Checked : {s['valid_fields']}/{s['total_fields_checked']} valid")
    print("─" * 70)

    # Validation Results
    print("  FIELD VALIDATION:")
    for v in report["validation_results"]:
        icon = "✅" if v["status"] == "VALID" else ("⬜" if v["status"] == "NOT_APPLICABLE" else "❌")
        print(f"    {icon} {v['field']:<35} {v['status']:<15} {v.get('value', '')[:30]}")

    # Missing Fields
    if report["missing_fields"]:
        print("─" * 70)
        print(f"  ⚠️  MISSING FIELDS ({len(report['missing_fields'])}):")
        for f in report["missing_fields"]:
            print(f"    • {f}")

    # Remarks
    print("─" * 70)
    print(f"  REMARKS: {report['remarks']}")
    print("═" * 70)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Food Product Label Validator — Legal Metrology Rules 2011"
    )
    parser.add_argument(
        "--product", type=str, default=None,
        help="Validate a specific product by name"
    )
    parser.add_argument(
        "--export-json", action="store_true",
        help="Export reports as JSON files"
    )
    args = parser.parse_args()

    # Load dataset
    if not os.path.exists(DATASET_PATH):
        print(f"❌ Dataset not found at: {DATASET_PATH}")
        sys.exit(1)

    products = load_dataset(DATASET_PATH)
    food_products = [p for p in products if p.get("category", "").lower() in ("food", "dairy")]

    if args.product:
        food_products = [
            p for p in food_products
            if args.product.lower() in p.get("product_name", "").lower()
        ]
        if not food_products:
            print(f"❌ No food product found matching: '{args.product}'")
            sys.exit(1)

    validator = FoodProductValidator()
    all_reports = []

    print("\n" + "█" * 70)
    print("  LEGAL METROLOGY FOOD PRODUCT COMPLIANCE VALIDATOR")
    print("  Legal Metrology (Packaged Commodities) Rules, 2011")
    print(f"  Products to validate: {len(food_products)}")
    print("█" * 70)

    for product in food_products:
        report = validator.validate_product(product)
        all_reports.append(report)
        print_report_summary(report)

    # ── Summary Statistics ────────────────────────────────────────────
    print("\n" + "█" * 70)
    print("  BATCH VALIDATION SUMMARY")
    print("█" * 70)

    total = len(all_reports)
    compliant = sum(1 for r in all_reports if r["compliance_summary"]["compliance_status"] == "FULLY_COMPLIANT")
    partial = sum(1 for r in all_reports if r["compliance_summary"]["compliance_status"] == "PARTIALLY_COMPLIANT")
    non_comp = sum(1 for r in all_reports if r["compliance_summary"]["compliance_status"] == "NON_COMPLIANT")
    avg_score = sum(r["compliance_summary"]["compliance_score"] for r in all_reports) / total if total else 0

    critical = sum(1 for r in all_reports if r["compliance_summary"]["risk_level"] == "CRITICAL")
    high = sum(1 for r in all_reports if r["compliance_summary"]["risk_level"] == "HIGH")

    print(f"  Total Products Validated : {total}")
    print(f"  ✅ Fully Compliant       : {compliant} ({compliant/total*100:.0f}%)" if total else "")
    print(f"  ⚠️  Partially Compliant  : {partial} ({partial/total*100:.0f}%)" if total else "")
    print(f"  ❌ Non-Compliant         : {non_comp} ({non_comp/total*100:.0f}%)" if total else "")
    print(f"  Average Score            : {avg_score:.1f}%")
    print(f"  🔴 Critical Risk         : {critical}")
    print(f"  🟠 High Risk             : {high}")
    print("█" * 70)

    # ── Export JSON ───────────────────────────────────────────────────
    if args.export_json:
        os.makedirs(REPORTS_DIR, exist_ok=True)
        output_path = os.path.join(
            REPORTS_DIR,
            f"food_compliance_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({
                "batch_summary": {
                    "total_products": total,
                    "compliant": compliant,
                    "partially_compliant": partial,
                    "non_compliant": non_comp,
                    "average_score": round(avg_score, 2),
                    "generated_at": datetime.now().isoformat(),
                },
                "reports": all_reports,
            }, f, indent=2, ensure_ascii=False)

        print(f"\n  📄 JSON report exported to: {output_path}")


if __name__ == "__main__":
    main()
