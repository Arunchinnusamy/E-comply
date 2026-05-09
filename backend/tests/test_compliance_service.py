"""
test_compliance_service.py
--------------------------
Unit tests for ComplianceService – no real Firebase calls.
"""

import pytest
import sys

# Ensure firebase stub is loaded before any app imports
import tests.conftest  # noqa: F401 – loads stub as side-effect


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def get_service():
    """Return a fresh ComplianceService instance."""
    # Clear cached modules so FirestoreService picks up the stub
    for mod in list(sys.modules.keys()):
        if mod.startswith("services"):
            del sys.modules[mod]
    from services.compliance_service import ComplianceService
    return ComplianceService()


@pytest.fixture
def service():
    return get_service()


@pytest.fixture
def full_product():
    return {
        "id": "prod-001",
        "name": "Test Biscuits",
        "brandName": "TestBrand",
        "category": "Food",
        "manufacturerName": "ABC Foods Pvt Ltd",
        "manufacturerAddress": "123 Industrial Area, Mumbai, MH 400001",
        "importerName": "N/A",
        "importerAddress": "N/A",
        "netQuantity": "200g",
        "mrp": "MRP Rs. 30",
        "manufacturingDate": "01/01/2025",
        "expiryDate": "01/01/2026",
        "batchNumber": "B2025-001",
        "customerCareDetails": "1800-123-4567",
        "countryOfOrigin": "India",
        "barcode": "8901234567890",
        "licenseNumber": "12345678901234",
    }


@pytest.fixture
def empty_product():
    return {
        "id": "prod-002",
        "name": "",
        "brandName": "",
        "category": "",
        "manufacturerName": "",
        "manufacturerAddress": "",
        "importerName": "",
        "importerAddress": "",
        "netQuantity": "",
        "mrp": "",
        "manufacturingDate": "",
        "expiryDate": "",
        "batchNumber": "",
        "customerCareDetails": "",
        "countryOfOrigin": "",
        "barcode": "",
        "licenseNumber": "",
    }


# ---------------------------------------------------------------------------
# Tests – mandatory field checking
# ---------------------------------------------------------------------------
class TestMandatoryFields:
    def test_all_fields_present_no_violations(self, service, full_product):
        missing, violations = service.check_mandatory_fields(full_product)
        assert missing == []
        assert violations == []

    def test_missing_all_fields(self, service, empty_product):
        missing, violations = service.check_mandatory_fields(empty_product)
        assert len(missing) == 16
        assert len(violations) == 16

    def test_partially_missing(self, service, full_product):
        full_product["manufacturerName"] = ""
        full_product["mrp"] = ""
        missing, violations = service.check_mandatory_fields(full_product)
        assert "Manufacturer Name" in missing
        assert "MRP" in missing
        assert len(missing) == 2  # only those two were blanked


# ---------------------------------------------------------------------------
# Tests – format validation
# ---------------------------------------------------------------------------
class TestFormatValidation:
    def test_valid_quantity_format(self, service, full_product):
        violations = service.validate_field_formats(full_product)
        # No format violations expected for a good product
        assert violations == []

    def test_invalid_quantity_unit(self, service, full_product):
        full_product["netQuantity"] = "200"  # missing unit
        violations = service.validate_field_formats(full_product)
        fields = [v["field"] for v in violations]
        assert "Net Quantity" in fields

    def test_invalid_mrp_format(self, service, full_product):
        full_product["mrp"] = "30"  # no MRP/Rs/₹ prefix
        violations = service.validate_field_formats(full_product)
        fields = [v["field"] for v in violations]
        assert "MRP" in fields

    def test_customer_care_email_accepted(self, service, full_product):
        full_product["customerCareDetails"] = "support@abcfoods.com"
        violations = service.validate_field_formats(full_product)
        assert all(v["field"] != "Customer Care Details" for v in violations)

    def test_customer_care_no_phone_or_email(self, service, full_product):
        full_product["customerCareDetails"] = "write to us"
        violations = service.validate_field_formats(full_product)
        fields = [v["field"] for v in violations]
        assert "Customer Care Details" in fields


# ---------------------------------------------------------------------------
# Tests – score calculation
# ---------------------------------------------------------------------------
class TestScoreCalculation:
    def test_full_score(self, service):
        assert service.calculate_compliance_score(16, 0, 0) == 100.0

    def test_zero_missing_with_format_violations(self, service):
        # 1 format violation → 5% penalty
        score = service.calculate_compliance_score(16, 0, 1)
        assert score == 95.0

    def test_one_missing_field(self, service):
        # (15/16)*100 = 93.75 – no extra format violations
        score = service.calculate_compliance_score(16, 1, 1)
        assert score == pytest.approx(93.75, abs=0.1)

    def test_all_missing(self, service):
        assert service.calculate_compliance_score(16, 16, 16) == 0.0

    def test_max_format_penalty_capped_at_20(self, service):
        # 5 format violations → penalty would be 25 but capped at 20
        score = service.calculate_compliance_score(16, 0, 5)
        assert score == 80.0


# ---------------------------------------------------------------------------
# Tests – compliance status
# ---------------------------------------------------------------------------
class TestStatus:
    def test_compliant(self, service):
        assert service.determine_status(100) == "COMPLIANT"

    def test_partial(self, service):
        assert service.determine_status(85) == "PARTIAL_COMPLIANT"

    def test_non_compliant(self, service):
        assert service.determine_status(60) == "NON_COMPLIANT"

    def test_boundary_70(self, service):
        assert service.determine_status(70) == "PARTIAL_COMPLIANT"


# ---------------------------------------------------------------------------
# Tests – risk level
# ---------------------------------------------------------------------------
class TestRiskLevel:
    def test_low_risk(self, service):
        assert service.determine_risk_level(95, []) == "LOW"

    def test_medium_risk(self, service):
        assert service.determine_risk_level(80, []) == "MEDIUM"

    def test_high_risk_score(self, service):
        assert service.determine_risk_level(60, []) == "HIGH"

    def test_critical_score(self, service):
        assert service.determine_risk_level(40, []) == "CRITICAL"

    def test_critical_due_to_violation_severity(self, service):
        violations = [{"severity": "CRITICAL", "field": "MRP", "description": "x", "ruleViolated": "y"}]
        assert service.determine_risk_level(90, violations) == "CRITICAL"


# ---------------------------------------------------------------------------
# Tests – full validate_product integration
# ---------------------------------------------------------------------------
class TestValidateProduct:
    def test_validate_compliant_product(self, service, full_product):
        report = service.validate_product(full_product)
        assert report["complianceScore"] == 100.0
        assert report["isCompliant"] is True
        assert report["complianceStatus"] == "COMPLIANT"
        assert report["riskLevel"] == "LOW"
        assert report["missingFields"] == []
        assert report["aiSummary"] != ""

    def test_validate_empty_product(self, service, empty_product):
        report = service.validate_product(empty_product)
        assert report["complianceScore"] == 0.0
        assert report["isCompliant"] is False
        assert report["complianceStatus"] == "NON_COMPLIANT"
        assert report["riskLevel"] == "CRITICAL"
        assert len(report["missingFields"]) == 16

    def test_report_has_id(self, service, full_product):
        report = service.validate_product(full_product)
        assert report["id"] != ""

    def test_recommendations_generated(self, service, empty_product):
        report = service.validate_product(empty_product)
        assert len(report["recommendations"]) > 0
