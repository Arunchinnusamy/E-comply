"""
compliance_analyzer.py
----------------------
Master orchestrator: OCR text → clean → categorise → validate 16 fields
→ score → risk → format into structured JSON report.

AI Model Integration:
    - Gemini API:     NLP-based field extraction + semantic validation
    - Random Forest:  ML-based risk prediction
    - Regex:          Rule-based fallback for all operations

This is the single entry-point the API layer calls for the full
compliance analysis pipeline.
"""

import logging
import re
import uuid
from datetime import datetime
from typing import Any

from services.text_cleaner_service import TextCleanerService
from services.category_service import CategoryService
from services.report_formatter_service import ReportFormatterService

logger = logging.getLogger(__name__)


class ComplianceAnalyzer:
    """End-to-end Legal Metrology compliance analysis pipeline."""

    def __init__(self, gemini_api_key: str = "", use_ml_risk: bool = True):
        self.cleaner = TextCleanerService()
        self.categoriser = CategoryService()
        self.formatter = ReportFormatterService()

        # ── AI Services (lazy, graceful fallback) ─────────────────────
        # Gemini NLP
        self.gemini = None
        if gemini_api_key:
            try:
                from services.gemini_service import GeminiService
                self.gemini = GeminiService(api_key=gemini_api_key)
                if self.gemini.is_available:
                    logger.info("ComplianceAnalyzer: Gemini NLP enabled")
                else:
                    logger.info("ComplianceAnalyzer: Gemini init failed, using regex")
                    self.gemini = None
            except Exception as e:
                logger.warning(f"Gemini init error: {e}")

        # ML Risk Prediction
        self.risk_service = None
        if use_ml_risk:
            try:
                from services.risk_prediction_service import RiskPredictionService
                self.risk_service = RiskPredictionService()
                if self.risk_service.is_ml_available:
                    logger.info("ComplianceAnalyzer: ML risk prediction enabled")
                else:
                    logger.info("ComplianceAnalyzer: ML model not found, rule-based risk")
            except Exception as e:
                logger.warning(f"Risk model init error: {e}")

    def analyze(self, ocr_text: str) -> dict[str, Any]:
        """
        Full pipeline: raw OCR text → structured compliance report JSON.

        Pipeline:
            1. Clean OCR text
            2. Extract fields (Gemini → regex fallback)
            3. Detect category
            4. Validate fields
            5. Calculate score
            6. Predict risk (ML → rule-based fallback)
            7. Generate remarks (Gemini → template fallback)
            8. Build structured report

        Args:
            ocr_text: Raw OCR-extracted text from product label

        Returns:
            dict: Structured compliance report in standard JSON format
        """
        # Step 1 — Clean OCR text
        cleaned = self.cleaner.clean(ocr_text)
        logger.info("Cleaned text length: %d", len(cleaned))

        # Step 2 — Extract all 16 fields (AI-enhanced)
        fields = self._extract_fields_smart(cleaned)

        # Step 3 — Detect category
        category = self.categoriser.detect_category(cleaned)
        fields["category"] = category

        # Step 4 — Validate fields & build results (Category-Aware)
        validation_results, missing = self.formatter.build_validation_results(fields, category)

        # Step 5 — Calculate score
        score = self.formatter.calculate_compliance_score(len(missing), total_fields=len(validation_results))

        # Step 6 — Predict risk (ML-enhanced)
        risk_prediction = self._predict_risk_smart(fields, category, score)
        risk = risk_prediction.get("risk_level", self.formatter.determine_risk_level(score))

        # Step 7 — Determine status
        status = self.formatter.determine_overall_status(score)

        # Step 8 — Generate remarks (AI-enhanced)
        remarks = self._generate_remarks_smart(
            product_name=fields.get("product_name", "Unknown Product"),
            category=category,
            score=score,
            risk_level=risk,
            missing_fields=missing,
        )

        # Step 9 — Build structured report
        report_id = f"RPT-{uuid.uuid4().hex[:8].upper()}"
        report = self.formatter.format_report(
            report_id=report_id,
            extracted_fields=fields,
            category=category,
            validation_results=validation_results,
            missing_fields=missing,
            compliance_score=score,
            risk_level=risk,
            overall_status=status,
            remarks=remarks,
        )

        # Attach AI metadata
        report["ai_metadata"] = {
            "gemini_enabled": self.gemini is not None and self.gemini.is_available,
            "ml_risk_enabled": self.risk_service is not None and self.risk_service.is_ml_available,
            "risk_prediction": risk_prediction,
            "extraction_method": "gemini+regex" if self.gemini and self.gemini.is_available else "regex",
        }

        logger.info(
            "Analysis complete: %s | score=%s | risk=%s | method=%s",
            report_id, score, risk,
            report["ai_metadata"]["extraction_method"],
        )
        return report

    # ──────────────────────────────────────────────────────────────────
    # Smart field extraction (Gemini + regex merge)
    # ──────────────────────────────────────────────────────────────────

    def _extract_fields_smart(self, text: str) -> dict[str, str]:
        """
        Extract fields using Gemini first, then fill gaps with regex.
        """
        # Always run regex as baseline
        regex_fields = self._extract_all_fields(text)

        # If Gemini available, merge with AI results
        if self.gemini and self.gemini.is_available:
            try:
                gemini_fields = self.gemini.extract_fields(text)

                # Merge: Gemini takes priority for non-empty values
                for key, value in gemini_fields.items():
                    if value and str(value).strip():
                        regex_fields[key] = str(value).strip()

                logger.info(
                    "Field merge: Gemini filled %d fields, regex filled remaining",
                    sum(1 for v in gemini_fields.values() if v),
                )
            except Exception as e:
                logger.warning(f"Gemini extraction failed, using regex only: {e}")

        return regex_fields

    # ──────────────────────────────────────────────────────────────────
    # Smart risk prediction (ML model + rule-based fallback)
    # ──────────────────────────────────────────────────────────────────

    def _predict_risk_smart(
        self, fields: dict, category: str, score: int
    ) -> dict[str, Any]:
        """Use ML model for risk prediction with rule-based fallback."""
        if self.risk_service:
            try:
                return self.risk_service.predict(fields, category)
            except Exception as e:
                logger.warning(f"ML risk prediction failed: {e}")

        # Fallback
        risk = self.formatter.determine_risk_level(score)
        return {"risk_level": risk, "confidence": 0.7, "method": "rule_based"}

    # ──────────────────────────────────────────────────────────────────
    # Smart remarks (Gemini → template fallback)
    # ──────────────────────────────────────────────────────────────────

    def _generate_remarks_smart(
        self,
        product_name: str,
        category: str,
        score: int,
        risk_level: str,
        missing_fields: list,
    ) -> str:
        """Generate remarks using Gemini, fallback to template."""
        if self.gemini and self.gemini.is_available:
            try:
                remarks = self.gemini.generate_remarks(
                    product_name=product_name,
                    category=category,
                    score=score,
                    risk_level=risk_level,
                    missing_fields=missing_fields,
                )
                if remarks:
                    return remarks
            except Exception as e:
                logger.warning(f"Gemini remarks failed: {e}")

        # Fallback to template
        return self.formatter.generate_remarks(
            product_name=product_name,
            category=category,
            score=score,
            risk_level=risk_level,
            missing_fields=missing_fields,
        )

    # ──────────────────────────────────────────────────────────────────
    # Regex field extraction (fallback / baseline)
    # ──────────────────────────────────────────────────────────────────

    def _extract_all_fields(self, text: str) -> dict[str, str]:
        """Extract all 16 mandatory fields from cleaned text."""
        f: dict[str, str] = {}

        f["product_name"] = self._extract_product_name(text)
        f["brand_name"] = self._extract_brand_name(text)
        f["manufacturer_name"] = self._extract_manufacturer_name(text)
        f["manufacturer_address"] = self._extract_manufacturer_address(text)
        f["importer_name"] = self._extract_importer_name(text)
        f["importer_address"] = self._extract_importer_address(text)
        f["mrp"] = self._extract_mrp(text)
        f["net_quantity"] = self._extract_net_quantity(text)
        f["manufacturing_date"] = self._extract_manufacturing_date(text)
        f["expiry_date"] = self._extract_expiry_date(text)
        f["batch_number"] = self._extract_batch_number(text)
        f["customer_care"] = self._extract_customer_care(text)
        f["country_of_origin"] = self._extract_country_of_origin(text)
        f["barcode"] = self._extract_barcode(text)
        f["license_number"] = self._extract_license_number(text)

        return f

    def _first_match(self, text: str, patterns: list[str]) -> str:
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE | re.MULTILINE)
            if m:
                return m.group(1).strip() if m.lastindex else m.group(0).strip()
        return ""

    def _extract_product_name(self, text: str) -> str:
        lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 3]
        return lines[0][:150] if lines else ""

    def _extract_brand_name(self, text: str) -> str:
        return self._first_match(text, [
            r'(?:Brand|Brand\s*Name)[:\s]+([^\n]{2,60})',
        ])

    def _extract_manufacturer_name(self, text: str) -> str:
        return self._first_match(text, [
            r'(?:Manufactured\s*By|Mfg\.?\s*By|Manufacturer)[:\s]+([^\n]{3,100})',
            r'(?:Marketed\s*By|Mkt\.?\s*By)[:\s]+([^\n]{3,100})',
            r'(?:Packed\s*By|Pkd\.?\s*By)[:\s]+([^\n]{3,100})',
        ])

    def _extract_manufacturer_address(self, text: str) -> str:
        return self._first_match(text, [
            r'(?:Regd\.?\s*Office|Address|Unit)[:\s]+([^\n]{10,200})',
            r'(?:Plot|Survey)\s*(?:No\.?)?[:\s]*([^\n]{10,200})',
        ])

    def _extract_importer_name(self, text: str) -> str:
        return self._first_match(text, [
            r'(?:Imported\s*By|Importer)[:\s]+([^\n]{3,100})',
        ])

    def _extract_importer_address(self, text: str) -> str:
        return self._first_match(text, [
            r'(?:Imported\s*By|Importer)[:\s]+[^\n]+\n([^\n]{10,200})',
        ])

    def _extract_mrp(self, text: str) -> str:
        return self._first_match(text, [
            r'(?:MRP|M\.R\.P\.?)[:\s]*[₹Rs.]*\s*([\d,]+\.?\d*)',
            r'₹\s*([\d,]+\.?\d*)',
            r'Rs\.?\s*([\d,]+\.?\d*)',
        ])

    def _extract_net_quantity(self, text: str) -> str:
        return self._first_match(text, [
            r'(?:Net\s*(?:Qty|Quantity|Wt|Weight|Vol|Volume|Content))[:\s]*([\d.]+\s*(?:kg|g|l|ml|pcs|units?|pieces?))',
            r'(\d+\.?\d*\s*(?:kg|g|l|ml))\b',
        ])

    def _extract_manufacturing_date(self, text: str) -> str:
        return self._first_match(text, [
            r'(?:Mfg\.?\s*(?:Date|Dt)?|Manufacturing\s*Date|Packed\s*(?:On|Date)|Packing\s*Date)[:\s]*([\d/\-.\s\w]{4,25})',
        ])

    def _extract_expiry_date(self, text: str) -> str:
        return self._first_match(text, [
            r'(?:Exp(?:iry)?\.?\s*(?:Date|Dt)?|Best\s*Before|Use\s*Before|BB)[:\s]*([\d/\-.\s\w]{4,25})',
        ])

    def _extract_batch_number(self, text: str) -> str:
        return self._first_match(text, [
            r'(?:Batch|Lot)\s*(?:No\.?|Number|#)?[:\s]*([A-Za-z0-9\-]{3,25})',
        ])

    def _extract_customer_care(self, text: str) -> str:
        phone = self._first_match(text, [
            r'(?:Customer\s*Care|Helpline|Toll\s*Free|Contact)[:\s]*([\d\s\-+()]{7,20})',
            r'(?:\+91|0)?[\s-]?\d{3}[\s-]?\d{3}[\s-]?\d{4}',
        ])
        email = self._first_match(text, [
            r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}',
        ])
        parts = [p for p in [phone, email] if p]
        return ", ".join(parts)

    def _extract_country_of_origin(self, text: str) -> str:
        return self._first_match(text, [
            r'(?:Country\s*of\s*Origin|Made\s*[iI]n)[:\s]*([A-Za-z\s]{3,30})',
            r'\b(India|China|USA|Germany|Japan|Korea|Thailand|Malaysia|Vietnam|Indonesia|Bangladesh|Sri Lanka|Nepal|Taiwan|Singapore)\b',
        ])

    def _extract_barcode(self, text: str) -> str:
        return self._first_match(text, [
            r'(?:Barcode|EAN|UPC|GTIN)[:\s]*(\d{8,13})',
            r'\b(\d{13})\b',
        ])

    def _extract_license_number(self, text: str) -> str:
        return self._first_match(text, [
            r'(?:FSSAI\s*(?:Lic\.?\s*)?(?:No\.?)?|License\s*(?:No\.?)?|Lic\.?\s*No\.?)[:\s]*([\d]{5,20})',
        ])
