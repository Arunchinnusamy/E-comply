"""
test_new_services.py
--------------------
Tests for the new services: ComplianceAnalyzer, CategoryService,
TextCleanerService, ReportFormatterService.
"""

import pytest
import sys

# Ensure stubs are loaded
import tests.conftest  # noqa: F401


def _fresh_import(module_name):
    """Force re-import to pick up stubs."""
    for mod in list(sys.modules.keys()):
        if mod.startswith("services"):
            del sys.modules[mod]
    return __import__(module_name, fromlist=[""])


# ---------------------------------------------------------------------------
# CategoryService tests
# ---------------------------------------------------------------------------
class TestCategoryService:
    @pytest.fixture
    def svc(self):
        mod = _fresh_import("services.category_service")
        return mod.CategoryService()

    def test_food_detected(self, svc):
        assert svc.detect_category("biscuits cream filled") == "Food"

    def test_cosmetics_detected(self, svc):
        assert svc.detect_category("shampoo for dry hair") == "Cosmetics"

    def test_electronics_detected(self, svc):
        assert svc.detect_category("USB charger cable") == "Electronics"

    def test_medical_detected(self, svc):
        assert svc.detect_category("tablet capsule dosage") == "Medical Products"

    def test_household_detected(self, svc):
        assert svc.detect_category("detergent powder floor cleaner") == "Household Products"

    def test_default_category(self, svc):
        assert svc.detect_category("random text nothing special") == "Packaged Goods"

    def test_empty_text(self, svc):
        assert svc.detect_category("") == "Packaged Goods"


# ---------------------------------------------------------------------------
# TextCleanerService tests
# ---------------------------------------------------------------------------
class TestTextCleanerService:
    @pytest.fixture
    def svc(self):
        mod = _fresh_import("services.text_cleaner_service")
        return mod.TextCleanerService()

    def test_removes_noise_chars(self, svc):
        text = "MRP Rs. 50§¶ Net Qty 200g"
        cleaned = svc.clean(text)
        assert "§" not in cleaned
        assert "¶" not in cleaned
        assert "MRP" in cleaned

    def test_removes_duplicate_lines(self, svc):
        text = "MRP Rs. 50\nMRP Rs. 50\nNet Qty 200g"
        cleaned = svc.clean(text)
        assert cleaned.count("MRP Rs. 50") == 1

    def test_removes_short_fragments(self, svc):
        text = "MRP Rs. 50\nA\n?\nNet Qty 200g"
        cleaned = svc.clean(text)
        assert "A\n" not in cleaned

    def test_empty_input(self, svc):
        assert svc.clean("") == ""

    def test_fixes_mrp_pattern(self, svc):
        text = "M.R.P. 100"
        cleaned = svc.clean(text)
        assert "MRP" in cleaned


# ---------------------------------------------------------------------------
# ReportFormatterService tests
# ---------------------------------------------------------------------------
class TestReportFormatterService:
    @pytest.fixture
    def svc(self):
        mod = _fresh_import("services.report_formatter_service")
        return mod.ReportFormatterService()

    def test_build_validation_results_all_present(self, svc):
        fields = {
            "product_name": "Biscuits",
            "brand_name": "TestBrand",
            "category": "Food",
            "manufacturer_name": "ABC Ltd",
            "manufacturer_address": "Mumbai",
            "importer_name": "N/A",
            "importer_address": "N/A",
            "mrp": "Rs. 30",
            "net_quantity": "200g",
            "manufacturing_date": "01/2025",
            "expiry_date": "01/2026",
            "batch_number": "B001",
            "customer_care": "1800-123-4567",
            "country_of_origin": "India",
            "barcode": "8901234567890",
            "license_number": "12345678901234",
        }
        results, missing = svc.build_validation_results(fields)
        assert len(results) == 16
        assert len(missing) == 0
        assert all(r["status"] == "Valid" for r in results)

    def test_build_validation_results_missing_fields(self, svc):
        fields = {"product_name": "Test", "mrp": "Rs. 50"}
        results, missing = svc.build_validation_results(fields)
        assert len(missing) == 14  # 16 - 2 present

    def test_compliance_score_full(self, svc):
        assert svc.calculate_compliance_score(0) == 100.0

    def test_compliance_score_half(self, svc):
        assert svc.calculate_compliance_score(8) == 50.0

    def test_risk_level_low(self, svc):
        assert svc.determine_risk_level(95.0) == "LOW"

    def test_risk_level_medium(self, svc):
        assert svc.determine_risk_level(75.0) == "MEDIUM"

    def test_risk_level_high(self, svc):
        assert svc.determine_risk_level(60.0) == "HIGH"

    def test_format_report_structure(self, svc):
        report = svc.format_report(
            report_id="RPT-TEST",
            extracted_fields={"product_name": "Test"},
            category="Food",
            validation_results=[{"field": "MRP", "status": "Valid"}],
            missing_fields=[],
            compliance_score=100.0,
            risk_level="LOW",
            overall_status="COMPLIANT",
            remarks="All good",
        )
        assert report["report_id"] == "RPT-TEST"
        assert report["product_details"]["category"] == "Food"
        assert report["compliance_summary"]["risk_level"] == "LOW"
        assert report["remarks"] == "All good"


# ---------------------------------------------------------------------------
# ComplianceAnalyzer integration tests
# ---------------------------------------------------------------------------
class TestComplianceAnalyzer:
    @pytest.fixture
    def analyzer(self):
        mod = _fresh_import("services.compliance_analyzer")
        return mod.ComplianceAnalyzer()

    def test_analyze_returns_structured_report(self, analyzer):
        ocr_text = """
        Premium Cookies
        Brand: TestBrand
        Manufactured By: ABC Foods Pvt Ltd
        Address: 123 Industrial Area, Mumbai 400001
        MRP Rs. 50
        Net Qty: 200g
        Mfg Date: 01/2025
        Exp Date: 01/2026
        Batch No: B2025-001
        Customer Care: 1800-123-4567
        Country of Origin: India
        FSSAI Lic No: 12345678901234
        8901234567890
        """
        report = analyzer.analyze(ocr_text)

        assert "report_id" in report
        assert report["report_id"].startswith("RPT-")
        assert "product_details" in report
        assert "compliance_summary" in report
        assert "validation_results" in report
        assert "missing_fields" in report
        assert "remarks" in report
        assert report["generated_date"] != ""

    def test_analyze_empty_text_returns_high_risk(self, analyzer):
        report = analyzer.analyze("")
        score = float(report["compliance_summary"]["compliance_score"])
        assert score < 70
        assert report["compliance_summary"]["risk_level"] == "HIGH"

    def test_category_detection_in_report(self, analyzer):
        report = analyzer.analyze("shampoo conditioner hair care beauty")
        assert report["product_details"]["category"] == "Cosmetics"
