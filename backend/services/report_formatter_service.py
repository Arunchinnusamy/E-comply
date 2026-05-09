"""
report_formatter_service.py
----------------------------
Transforms internal compliance data into the structured JSON report
format required by the Legal Metrology Compliance Validation System.

Produces clean, professional output suitable for:
    - Android UI display
    - PDF export
    - Inspector / government reports
"""

import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class ReportFormatterService:
    """Format compliance validation results into the standard report JSON."""

    # All 16 mandatory fields and their display names
    MANDATORY_FIELDS = [
        ("Product Name", "product_name"),
        ("Brand Name", "brand_name"),
        ("Category", "category"),
        ("Manufacturer Name", "manufacturer_name"),
        ("Manufacturer Address", "manufacturer_address"),
        ("Importer Name", "importer_name"),
        ("Importer Address", "importer_address"),
        ("MRP", "mrp"),
        ("Net Quantity", "net_quantity"),
        ("Manufacturing Date", "manufacturing_date"),
        ("Expiry Date", "expiry_date"),
        ("Batch Number", "batch_number"),
        ("Customer Care Details", "customer_care"),
        ("Country of Origin", "country_of_origin"),
        ("Barcode / QR Code", "barcode"),
        ("License Number", "license_number"),
    ]

    def format_report(
        self,
        report_id: str,
        extracted_fields: dict[str, str],
        category: str,
        validation_results: list[dict[str, str]],
        missing_fields: list[str],
        compliance_score: float,
        risk_level: str,
        overall_status: str,
        remarks: str = "",
    ) -> dict[str, Any]:
        """
        Build the standard structured JSON compliance report.

        Args:
            report_id: Unique report identifier
            extracted_fields: Dict of field_key → extracted value
            category: Detected product category
            validation_results: List of {field, status} dicts
            missing_fields: List of missing mandatory field names
            compliance_score: Numeric score 0–100
            risk_level: LOW / MEDIUM / HIGH
            overall_status: COMPLIANT / PARTIAL_COMPLIANT / NON_COMPLIANT
            remarks: AI-generated summary / remarks

        Returns:
            dict: Clean structured report JSON
        """
        f = extracted_fields  # shorthand

        report = {
            "report_id": report_id,
            "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

            "product_details": {
                "product_name": f.get("product_name", ""),
                "brand_name": f.get("brand_name", ""),
                "category": category,
            },

            "manufacturer_details": {
                "name": f.get("manufacturer_name", ""),
                "address": f.get("manufacturer_address", ""),
            },

            "importer_details": {
                "name": f.get("importer_name", ""),
                "address": f.get("importer_address", ""),
            },

            "pricing_details": {
                "mrp": f.get("mrp", ""),
                "net_quantity": f.get("net_quantity", ""),
            },

            "date_details": {
                "manufacturing_date": f.get("manufacturing_date", ""),
                "expiry_date": f.get("expiry_date", ""),
            },

            "product_identification": {
                "batch_number": f.get("batch_number", ""),
                "barcode": f.get("barcode", ""),
                "license_number": f.get("license_number", ""),
            },

            "customer_support": {
                "customer_care": f.get("customer_care", ""),
            },

            "country_of_origin": f.get("country_of_origin", ""),

            "validation_results": validation_results,

            "missing_fields": missing_fields,

            "compliance_summary": {
                "compliance_score": str(round(compliance_score, 2)),
                "risk_level": risk_level,
                "overall_status": overall_status,
            },

            "remarks": remarks,
        }

        return report

    def build_validation_results(
        self, extracted_fields: dict[str, str], category: str = "Packaged Goods"
    ) -> tuple[list[dict[str, str]], list[str]]:
        """
        Validate all 16 mandatory fields + category-specific rules.
        """
        validation_results: list[dict[str, str]] = []
        missing_fields: list[str] = []

        # 1. Start with 16 Global Mandatory Fields
        current_rules = list(self.MANDATORY_FIELDS)

        # 2. Add Category-Specific Rules
        if category == "Food":
            current_rules.append(("FSSAI License", "license_number"))
            current_rules.append(("Nutritional Information", "nutritional_info"))
            current_rules.append(("Veg/Non-Veg Logo", "veg_nonveg"))
        elif category == "Electronics":
            current_rules.append(("BIS Registration", "bis_number"))
            current_rules.append(("Voltage/Power Rating", "power_rating"))
        elif category == "Cosmetics":
            current_rules.append(("Ingredients List", "ingredients"))
            current_rules.append(("Use Before Date", "expiry_date"))
        elif category == "Medical Products":
            current_rules.append(("Drug License", "drug_license"))
            current_rules.append(("Schedule H Warning", "schedule_h"))

        # 3. Perform Validation
        seen_fields = set()
        for display_name, field_key in current_rules:
            # Avoid duplicate checks for the same display name
            if display_name in seen_fields: continue
            seen_fields.add(display_name)
            
            value = extracted_fields.get(field_key, "").strip()

            if value:
                status = "Valid"
            else:
                status = "Missing"
                missing_fields.append(display_name)

            validation_results.append({
                "field": display_name,
                "status": status,
                "category_rule": "Standard" if display_name in dict(self.MANDATORY_FIELDS) else "Category-Specific"
            })

        return validation_results, missing_fields

    def calculate_compliance_score(
        self, missing_count: int, total_fields: int = 16
    ) -> float:
        """
        Calculate compliance score.

        Each valid field increases score proportionally.
        Missing mandatory fields reduce score.

        Args:
            missing_count: Number of missing mandatory fields
            total_fields: Total mandatory fields (default 16)

        Returns:
            float: Score 0–100
        """
        if total_fields == 0:
            return 100.0
        valid_count = total_fields - missing_count
        return round((valid_count / total_fields) * 100, 2)

    def determine_risk_level(self, score: float) -> str:
        """
        Determine risk level per the defined thresholds.

        90–100 → LOW RISK
        70–89  → MEDIUM RISK
        Below 70 → HIGH RISK
        """
        if score >= 90:
            return "LOW"
        elif score >= 70:
            return "MEDIUM"
        else:
            return "HIGH"

    def determine_overall_status(self, score: float) -> str:
        """Map score to compliance status label."""
        if score >= 90:
            return "COMPLIANT"
        elif score >= 70:
            return "PARTIAL_COMPLIANT"
        else:
            return "NON_COMPLIANT"

        return " ".join(parts)

    def generate_professional_text_report(self, report: dict[str, Any]) -> str:
        """
        Convert the structured JSON report into a professional, human-readable
        plain text report as requested for the demo.
        """
        p = report["product_details"]
        m = report["manufacturer_details"]
        pr = report["pricing_details"]
        d = report["date_details"]
        i = report["product_identification"]
        v = report["validation_results"]
        s = report["compliance_summary"]

        # Helper to get validation status icon
        def get_status(field_name: str) -> str:
            for item in v:
                if item["field"].lower() == field_name.lower():
                    return "✔" if item["status"] == "Valid" else "✘"
            return "✘"

        text = [
            "LEGAL METROLOGY COMPLIANCE REPORT",
            "-----------------------------------",
            "",
            "Product Details:",
            f"- Product Name: {p['product_name']}",
            f"- Brand Name: {p['brand_name']}",
            f"- Category: {p['category']}",
            "",
            "Manufacturer Details:",
            f"- Manufacturer: {m['name']}",
            f"- Address: {m['address']}",
            "",
            "Pricing Details:",
            f"- MRP: {pr['mrp']}",
            f"- Net Quantity: {pr['net_quantity']}",
            "",
            "Date Details:",
            f"- Manufacturing Date: {d['manufacturing_date']}",
            f"- Expiry Date: {d['expiry_date']}",
            "",
            "Product Identification:",
            f"- Batch Number: {i['batch_number']}",
            f"- Barcode: {i['barcode']}",
            f"- License Number: {i['license_number']}",
            "",
            "Validation Results:",
            f"{get_status('MRP')} MRP Validation",
            f"{get_status('Manufacturer Name')} Manufacturer Validation",
            f"{get_status('Net Quantity')} Quantity Validation",
            f"{get_status('Expiry Date')} Expiry Validation",
            f"{get_status('Barcode / QR Code')} Barcode Validation",
            "",
            "Missing Fields:",
        ]

        if report["missing_fields"]:
            for field in report["missing_fields"]:
                text.append(f"- {field}")
        else:
            text.append("- None (All mandatory fields present)")

        text.extend([
            "",
            "Compliance Summary:",
            f"- Compliance Score: {s['compliance_score']}/100",
            f"- Risk Level: {s['risk_level']} RISK",
            f"- Overall Status: {s['overall_status']}",
            "",
            "AI Remarks:",
            f"- {report['remarks']}",
            "",
            "-----------------------------------",
            f"Generated on: {report['generated_date']}",
            f"Report ID: {report['report_id']}"
        ])

        return "\n".join(text)

