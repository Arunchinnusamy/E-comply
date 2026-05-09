"""
gemini_service.py
─────────────────
Google Gemini API integration for intelligent NLP-based field
extraction and compliance validation.

Features:
    - Structured field extraction from OCR text
    - Semantic validation of extracted field values
    - AI-generated compliance remarks and recommendations
    - Fallback-safe: returns empty results on API failure

Requires:
    pip install google-generativeai
    Set GEMINI_API_KEY in .env
"""

import json
import logging
import re
from typing import Any, Optional

logger = logging.getLogger(__name__)


class GeminiService:
    """Google Gemini API client for NLP-powered compliance validation."""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.model = None
        self._initialized = False

        if api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel("gemini-1.5-flash")
                self._initialized = True
                logger.info("GeminiService initialized with Gemini 1.5 Flash")
            except ImportError:
                logger.warning(
                    "google-generativeai not installed. "
                    "Run: pip install google-generativeai"
                )
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
        else:
            logger.info(
                "GeminiService: No API key provided — NLP features disabled"
            )

    @property
    def is_available(self) -> bool:
        return self._initialized and self.model is not None

    # ══════════════════════════════════════════════════════════════════════
    # 1. Structured Field Extraction
    # ══════════════════════════════════════════════════════════════════════

    def extract_fields(self, ocr_text: str) -> dict[str, Any]:
        """
        Use Gemini as an AI-powered Legal Metrology Compliance Validator.
        Performs extraction, validation, scoring, and risk assessment in one pass.
        """
        if not self.is_available:
            return {}

        prompt = f"""You are an AI-powered Legal Metrology Compliance Validator.
Your task is to analyze OCR extracted product label text and generate a structured Legal Metrology Compliance Report.

Instructions:
1. Read the OCR extracted text carefully.
2. Identify and extract mandatory legal metrology fields.
3. Validate based on Legal Metrology Packaged Commodities Rules 2011.
4. Calculate a compliance score out of 100.
5. Assign risk level: LOW (90+), MEDIUM (70-89), HIGH (Below 70 or critical violations like Expiry).

Examples of your expected logic:

- Product: Aachi Chilli Powder | Category: Food | Status: Valid | Score: 95 | Risk: LOW
  (All fields like MRP, Mfg Date, Expiry, Batch, Mfd Address are present and valid)

- Product: Fake Herbal Oil | Category: Cosmetics | Status: Invalid | Score: 45 | Risk: HIGH
  (Missing Manufacturer Name, Address, and Expiry Date)

- Product: Expired Juice | Category: Food | Status: Invalid | Score: 50 | Risk: HIGH
  (Date validation failure: Current date is past the extracted Expiry Date)

- Product: Samsung Charger | Category: Electronics | Status: Valid | Score: 88 | Risk: MEDIUM
  (Manufacturer and MRP present; Electronics often don't have Expiry dates)

JSON Format to return:
{
  "product_name": "",
  "brand_name": "",
  "category": "",
  "manufacturer_details": { "name": "", "address": "" },
  "importer_details": { "name": "", "address": "" },
  "pricing_details": { "mrp": "", "net_quantity": "" },
  "date_details": { "manufacturing_date": "", "expiry_date": "" },
  "product_identification": { "batch_number": "", "barcode": "", "license_number": "" },
  "customer_support": { "customer_care": "" },
  "country_of_origin": "",
  "validation_results": {
    "mrp_present": "Yes/No",
    "mfd_details_present": "Yes/No",
    "net_quantity_valid": "Yes/No",
    "expiry_date_valid": "Yes/No",
    "batch_number_present": "Yes/No"
  },
  "missing_fields": [],
  "compliance_score": 0,
  "risk_level": "LOW/MEDIUM/HIGH",
  "overall_status": "COMPLIANT/NON_COMPLIANT",
  "remarks": "Professional summary based on Rules 2011"
}
"""

    def extract_fields(self, ocr_text: str) -> dict[str, Any]:
        """
        Use Gemini as an AI-powered Legal Metrology Compliance Validator.
        Performs extraction, validation, scoring, and risk assessment in one pass.
        """
        if not self.is_available:
            return {}

        prompt = f"""{self._get_system_prompt()}

OCR Text:
\"\"\"
{ocr_text}
\"\"\"

Return ONLY the JSON, no markdown, no extra text."""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()

            # Clean markdown code fences if present
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)

            fields = json.loads(text)
            logger.info(f"Gemini extracted {sum(1 for v in fields.values() if v)} fields")
            return fields

        except json.JSONDecodeError as e:
            logger.error(f"Gemini returned invalid JSON: {e}")
            return {}
        except Exception as e:
            logger.error(f"Gemini field extraction failed: {e}")
            return {}

    def full_analysis(self, ocr_text: str) -> dict[str, Any]:
        """
        Run the complete AI validation pipeline in a single pass.
        """
        if not self.is_available:
            return {
                "gemini_available": False,
                "report": {}
            }

        report = self.extract_fields(ocr_text)

        return {
            "gemini_available": True,
            "report": report
        }
