"""
seed_firestore.py
─────────────────
Seeds the Firestore collections with initial data:
  - rules/       → Legal Metrology Rules 2011 definitions
  - categories/  → Product category definitions with field requirements

Run once to initialise the database:
    python seed_firestore.py

Safe to re-run — uses set() which overwrites existing docs.
"""

import os
import sys
import logging

# Ensure we can import from the backend package
sys.path.insert(0, os.path.dirname(__file__))

import firebase_admin
from firebase_admin import credentials
from config import Config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ─── Firebase init ────────────────────────────────────────────────────────────
if not firebase_admin._apps:
    cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)

from services.firestore_service import FirestoreService

db = FirestoreService()


# ═══════════════════════════════════════════════════════════════════════════════
# RULES COLLECTION — Legal Metrology (Packaged Commodities) Rules, 2011
# ═══════════════════════════════════════════════════════════════════════════════

RULES = [
    {
        "ruleId": "rule_product_name",
        "fieldName": "Product Name",
        "section": "Rule 6(1)(a)",
        "description": "Name or description of the commodity contained in the package",
        "isMandatory": True,
        "applicableCategories": ["Food", "FMCG", "Cosmetics", "Pharma", "Electronics", "Dairy", "Pet Care", "Stationery"],
        "validationPattern": None,
        "errorMessage": "Product name is missing from the label",
        "severity": "HIGH",
        "penaltyInfo": "First offence: ₹25,000. Second offence: ₹50,000. Section 36, Legal Metrology Act 2009",
        "isActive": True,
    },
    {
        "ruleId": "rule_manufacturer_name",
        "fieldName": "Manufacturer Name",
        "section": "Rule 6(1)(b)",
        "description": "Name and complete address of the manufacturer, packer, or importer",
        "isMandatory": True,
        "applicableCategories": ["Food", "FMCG", "Cosmetics", "Pharma", "Electronics", "Dairy", "Pet Care", "Stationery"],
        "validationPattern": None,
        "errorMessage": "Manufacturer name is missing from the label",
        "severity": "CRITICAL",
        "penaltyInfo": "First offence: ₹25,000. Second offence: ₹50,000. Section 36, Legal Metrology Act 2009",
        "isActive": True,
    },
    {
        "ruleId": "rule_manufacturer_address",
        "fieldName": "Manufacturer Address",
        "section": "Rule 6(1)(b)",
        "description": "Complete address of manufacturer including pin code",
        "isMandatory": True,
        "applicableCategories": ["Food", "FMCG", "Cosmetics", "Pharma", "Electronics", "Dairy", "Pet Care", "Stationery"],
        "validationPattern": None,
        "errorMessage": "Manufacturer address is missing from the label",
        "severity": "HIGH",
        "penaltyInfo": "First offence: ₹25,000. Section 36, Legal Metrology Act 2009",
        "isActive": True,
    },
    {
        "ruleId": "rule_net_quantity",
        "fieldName": "Net Quantity",
        "section": "Rule 6(1)(c)",
        "description": "Net quantity by weight, measure, or number in standard metric units",
        "isMandatory": True,
        "applicableCategories": ["Food", "FMCG", "Cosmetics", "Pharma", "Electronics", "Dairy", "Pet Care"],
        "validationPattern": "\\d+\\s*(kg|g|l|ml|unit|pcs|piece)",
        "errorMessage": "Net quantity is missing or invalid. Must include value and unit (kg/g/l/ml)",
        "severity": "CRITICAL",
        "penaltyInfo": "First offence: ₹25,000. Second offence: ₹50,000. Section 36, Legal Metrology Act 2009",
        "isActive": True,
    },
    {
        "ruleId": "rule_manufacturing_date",
        "fieldName": "Manufacturing/Packing Date",
        "section": "Rule 6(1)(d)",
        "description": "Month and year in which the commodity is manufactured, packed, or imported",
        "isMandatory": True,
        "applicableCategories": ["Food", "FMCG", "Cosmetics", "Pharma", "Dairy"],
        "validationPattern": None,
        "errorMessage": "Manufacturing or packing date is missing",
        "severity": "HIGH",
        "penaltyInfo": "First offence: ₹25,000. Section 36, Legal Metrology Act 2009",
        "isActive": True,
    },
    {
        "ruleId": "rule_expiry_date",
        "fieldName": "Expiry Date",
        "section": "Rule 6(1)(e)",
        "description": "Best before or use by date for perishable commodities",
        "isMandatory": True,
        "applicableCategories": ["Food", "Pharma", "Cosmetics", "Dairy"],
        "validationPattern": None,
        "errorMessage": "Expiry / best before date is missing",
        "severity": "CRITICAL",
        "penaltyInfo": "First offence: ₹25,000. Second offence: ₹50,000. Section 36, Legal Metrology Act 2009",
        "isActive": True,
    },
    {
        "ruleId": "rule_mrp",
        "fieldName": "MRP",
        "section": "Rule 6(1)(f)",
        "description": "Maximum Retail Price (MRP) inclusive of all taxes",
        "isMandatory": True,
        "applicableCategories": ["Food", "FMCG", "Cosmetics", "Pharma", "Electronics", "Dairy", "Pet Care", "Stationery"],
        "validationPattern": "(?:MRP|Rs\\.?|₹)\\s*\\d+",
        "errorMessage": "MRP is missing from the label",
        "severity": "CRITICAL",
        "penaltyInfo": "First offence: ₹25,000. Second offence: ₹50,000. Section 36, Legal Metrology Act 2009",
        "isActive": True,
    },
    {
        "ruleId": "rule_importer_name",
        "fieldName": "Importer Name",
        "section": "Rule 6(1)(g)",
        "description": "Name and address of importer for imported products",
        "isMandatory": True,
        "applicableCategories": ["Food", "FMCG", "Cosmetics", "Pharma", "Electronics", "Dairy", "Pet Care", "Stationery"],
        "validationPattern": None,
        "errorMessage": "Importer name is missing (required for imported products)",
        "severity": "HIGH",
        "penaltyInfo": "First offence: ₹25,000. Section 36, Legal Metrology Act 2009",
        "isActive": True,
    },
    {
        "ruleId": "rule_importer_address",
        "fieldName": "Importer Address",
        "section": "Rule 6(1)(g)",
        "description": "Complete address of the importer",
        "isMandatory": True,
        "applicableCategories": ["Food", "FMCG", "Cosmetics", "Pharma", "Electronics", "Dairy", "Pet Care", "Stationery"],
        "validationPattern": None,
        "errorMessage": "Importer address is missing (required for imported products)",
        "severity": "HIGH",
        "penaltyInfo": "First offence: ₹25,000. Section 36, Legal Metrology Act 2009",
        "isActive": True,
    },
    {
        "ruleId": "rule_customer_care",
        "fieldName": "Customer Care Details",
        "section": "Rule 6(1)(h)",
        "description": "Customer care details — email or toll-free/landline number",
        "isMandatory": True,
        "applicableCategories": ["Food", "FMCG", "Cosmetics", "Pharma", "Electronics", "Dairy", "Pet Care", "Stationery"],
        "validationPattern": None,
        "errorMessage": "Customer care contact details are missing",
        "severity": "HIGH",
        "penaltyInfo": "First offence: ₹25,000. Section 36, Legal Metrology Act 2009",
        "isActive": True,
    },
    {
        "ruleId": "rule_country_of_origin",
        "fieldName": "Country of Origin",
        "section": "Rule 6(1)(g)",
        "description": "Country of origin — mandatory for all imported products",
        "isMandatory": True,
        "applicableCategories": ["Food", "FMCG", "Cosmetics", "Pharma", "Electronics", "Dairy", "Pet Care", "Stationery"],
        "validationPattern": None,
        "errorMessage": "Country of origin is missing",
        "severity": "HIGH",
        "penaltyInfo": "First offence: ₹25,000. Section 36, Legal Metrology Act 2009",
        "isActive": True,
    },
    {
        "ruleId": "rule_brand_name",
        "fieldName": "Brand Name",
        "section": "Rule 6(1)(a)",
        "description": "Brand or trade name of the commodity",
        "isMandatory": True,
        "applicableCategories": ["Food", "FMCG", "Cosmetics", "Pharma", "Electronics", "Dairy", "Pet Care", "Stationery"],
        "validationPattern": None,
        "errorMessage": "Brand name is missing",
        "severity": "MEDIUM",
        "penaltyInfo": "First offence: ₹10,000. Section 36, Legal Metrology Act 2009",
        "isActive": True,
    },
    {
        "ruleId": "rule_batch_number",
        "fieldName": "Batch Number",
        "section": "Rule 6(2)",
        "description": "Batch or lot number for traceability",
        "isMandatory": False,
        "applicableCategories": ["Food", "Pharma", "Cosmetics", "Dairy"],
        "validationPattern": "[A-Za-z0-9\\-]{3,25}",
        "errorMessage": "Batch number is recommended for traceability",
        "severity": "LOW",
        "penaltyInfo": "Advisory — no direct penalty",
        "isActive": True,
    },
    {
        "ruleId": "rule_barcode",
        "fieldName": "Barcode / QR Code",
        "section": "Rule 6(3)",
        "description": "Unique barcode or QR code for product identification",
        "isMandatory": False,
        "applicableCategories": ["Food", "FMCG", "Cosmetics", "Pharma", "Electronics", "Dairy", "Pet Care", "Stationery"],
        "validationPattern": "\\d{8,13}",
        "errorMessage": "Barcode recommended for product identification",
        "severity": "LOW",
        "penaltyInfo": "Advisory — no direct penalty",
        "isActive": True,
    },
    {
        "ruleId": "rule_license_number",
        "fieldName": "License Number",
        "section": "FSS Act 2006, Section 31",
        "description": "FSSAI license number — mandatory for all food business operators",
        "isMandatory": True,
        "applicableCategories": ["Food", "Dairy"],
        "validationPattern": "\\d{5,20}",
        "errorMessage": "FSSAI license number is missing (mandatory for food products)",
        "severity": "CRITICAL",
        "penaltyInfo": "Up to ₹5,00,000 fine. FSS Act 2006, Section 63",
        "isActive": True,
    },
    {
        "ruleId": "rule_drug_license",
        "fieldName": "Drug License Number",
        "section": "Drugs and Cosmetics Act, 1940",
        "description": "Drug manufacturing license number",
        "isMandatory": True,
        "applicableCategories": ["Pharma"],
        "validationPattern": None,
        "errorMessage": "Drug license number is missing",
        "severity": "CRITICAL",
        "penaltyInfo": "Imprisonment up to 3 years or fine. Drugs and Cosmetics Act Section 27",
        "isActive": True,
    },
]


# ═══════════════════════════════════════════════════════════════════════════════
# CATEGORIES COLLECTION
# ═══════════════════════════════════════════════════════════════════════════════

CATEGORIES = [
    {
        "categoryId": "food",
        "name": "Food",
        "displayName": "Food & Beverages",
        "description": "Packaged food products, beverages, spices, condiments, snacks",
        "mandatoryFields": [
            "Product Name", "Brand Name", "Manufacturer Name", "Manufacturer Address",
            "MRP", "Net Quantity", "Manufacturing/Packing Date", "Expiry Date",
            "Customer Care Details", "Country of Origin", "FSSAI License Number",
        ],
        "optionalFields": ["Batch Number", "Barcode / QR Code", "Importer Name", "Importer Address"],
        "additionalLicenses": ["FSSAI"],
        "riskWeight": 1.5,
        "isActive": True,
        "iconName": "restaurant",
    },
    {
        "categoryId": "dairy",
        "name": "Dairy",
        "displayName": "Dairy Products",
        "description": "Milk, butter, cheese, ghee, curd, paneer, ice cream",
        "mandatoryFields": [
            "Product Name", "Brand Name", "Manufacturer Name", "Manufacturer Address",
            "MRP", "Net Quantity", "Manufacturing/Packing Date", "Expiry Date",
            "Customer Care Details", "Country of Origin", "FSSAI License Number",
        ],
        "optionalFields": ["Batch Number", "Barcode / QR Code"],
        "additionalLicenses": ["FSSAI"],
        "riskWeight": 1.8,
        "isActive": True,
        "iconName": "local_drink",
    },
    {
        "categoryId": "fmcg",
        "name": "FMCG",
        "displayName": "Fast-Moving Consumer Goods",
        "description": "Detergents, soaps, cleaners, toiletries, personal care items",
        "mandatoryFields": [
            "Product Name", "Brand Name", "Manufacturer Name", "Manufacturer Address",
            "MRP", "Net Quantity", "Manufacturing/Packing Date",
            "Customer Care Details", "Country of Origin",
        ],
        "optionalFields": ["Expiry Date", "Batch Number", "Barcode / QR Code", "BIS Certification"],
        "additionalLicenses": ["BIS"],
        "riskWeight": 1.0,
        "isActive": True,
        "iconName": "shopping_cart",
    },
    {
        "categoryId": "cosmetics",
        "name": "Cosmetics",
        "displayName": "Cosmetics & Personal Care",
        "description": "Skincare, haircare, makeup, deodorants, perfumes",
        "mandatoryFields": [
            "Product Name", "Brand Name", "Manufacturer Name", "Manufacturer Address",
            "MRP", "Net Quantity", "Manufacturing/Packing Date", "Expiry Date",
            "Customer Care Details", "Country of Origin",
        ],
        "optionalFields": ["Batch Number", "Barcode / QR Code", "Ingredients List"],
        "additionalLicenses": ["CDSCO"],
        "riskWeight": 1.2,
        "isActive": True,
        "iconName": "face",
    },
    {
        "categoryId": "pharma",
        "name": "Pharma",
        "displayName": "Pharmaceutical & OTC",
        "description": "Over-the-counter medicines, pain relief, health supplements",
        "mandatoryFields": [
            "Product Name", "Brand Name", "Manufacturer Name", "Manufacturer Address",
            "MRP", "Net Quantity", "Manufacturing/Packing Date", "Expiry Date",
            "Customer Care Details", "Country of Origin", "Drug License Number",
            "Batch Number",
        ],
        "optionalFields": ["Barcode / QR Code"],
        "additionalLicenses": ["Drug License", "CDSCO"],
        "riskWeight": 2.0,
        "isActive": True,
        "iconName": "medical_services",
    },
    {
        "categoryId": "electronics",
        "name": "Electronics",
        "displayName": "Electronics & Electrical",
        "description": "Batteries, chargers, cables, adapters, small electronics",
        "mandatoryFields": [
            "Product Name", "Brand Name", "Manufacturer Name", "Manufacturer Address",
            "MRP", "Net Quantity", "Manufacturing/Packing Date",
            "Customer Care Details", "Country of Origin",
        ],
        "optionalFields": ["Expiry Date", "Barcode / QR Code", "BIS/ISI Certification"],
        "additionalLicenses": ["BIS"],
        "riskWeight": 1.0,
        "isActive": True,
        "iconName": "electrical_services",
    },
    {
        "categoryId": "pet_care",
        "name": "Pet Care",
        "displayName": "Pet Food & Care",
        "description": "Pet food, treats, grooming products",
        "mandatoryFields": [
            "Product Name", "Brand Name", "Manufacturer Name", "Manufacturer Address",
            "MRP", "Net Quantity", "Manufacturing/Packing Date", "Expiry Date",
            "Customer Care Details", "Country of Origin",
        ],
        "optionalFields": ["Batch Number", "Barcode / QR Code", "FSSAI License Number"],
        "additionalLicenses": [],
        "riskWeight": 1.0,
        "isActive": True,
        "iconName": "pets",
    },
    {
        "categoryId": "stationery",
        "name": "Stationery",
        "displayName": "Stationery & Office",
        "description": "Pens, pencils, notebooks, adhesives, office supplies",
        "mandatoryFields": [
            "Product Name", "Brand Name", "Manufacturer Name", "Manufacturer Address",
            "MRP", "Net Quantity", "Customer Care Details", "Country of Origin",
        ],
        "optionalFields": ["Manufacturing/Packing Date", "Barcode / QR Code"],
        "additionalLicenses": [],
        "riskWeight": 0.5,
        "isActive": True,
        "iconName": "edit",
    },
]


def seed():
    """Seed rules and categories into Firestore."""
    print("\n" + "=" * 60)
    print("  E-COMPLY — FIRESTORE SEEDER")
    print("=" * 60)

    # ── Seed Rules ────────────────────────────────────────────────────
    print(f"\n📜 Seeding {len(RULES)} rules into '{db.RULES_COLLECTION}'...")
    rules_ok = 0
    for rule in RULES:
        if db.save_rule(rule):
            rules_ok += 1
            print(f"  ✅ {rule['ruleId']:<30} {rule['fieldName']}")
        else:
            print(f"  ❌ {rule['ruleId']:<30} FAILED")
    print(f"  → {rules_ok}/{len(RULES)} rules seeded")

    # ── Seed Categories ───────────────────────────────────────────────
    print(f"\n📂 Seeding {len(CATEGORIES)} categories into '{db.CATEGORIES_COLLECTION}'...")
    cats_ok = 0
    for cat in CATEGORIES:
        if db.save_category(cat):
            cats_ok += 1
            print(f"  ✅ {cat['categoryId']:<20} {cat['displayName']}")
        else:
            print(f"  ❌ {cat['categoryId']:<20} FAILED")
    print(f"  → {cats_ok}/{len(CATEGORIES)} categories seeded")

    # ── Summary ───────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"  DONE — Rules: {rules_ok}, Categories: {cats_ok}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    seed()
