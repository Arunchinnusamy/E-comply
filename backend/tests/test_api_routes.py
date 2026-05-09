"""
test_api_routes.py
------------------
Integration tests for Flask API routes using the test client.
Firebase and Firestore are fully stubbed (see conftest.py).
"""

import json
import pytest


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
class TestHealth:
    def test_health_returns_200(self, client):
        res = client.get("/health")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "healthy"


# ---------------------------------------------------------------------------
# Auth protection
# ---------------------------------------------------------------------------
class TestAuthProtection:
    PROTECTED_ROUTES = [
        ("/api/ocr/extract", "POST"),
        ("/api/compliance/validate", "POST"),
        ("/api/reports/some-id", "GET"),
        ("/api/reports/user/uid-123", "GET"),
        ("/api/reports/inspector", "GET"),
        ("/api/ecommerce/scrape", "POST"),
    ]

    def test_missing_auth_returns_401(self, client):
        for route, method in self.PROTECTED_ROUTES:
            fn = client.post if method == "POST" else client.get
            res = fn(route, content_type="application/json")
            assert res.status_code == 401, f"Expected 401 for {method} {route}"

    def test_invalid_token_returns_401(self, client):
        headers = {"Authorization": "Bearer bad-token"}
        res = client.get("/api/reports/inspector", headers=headers)
        assert res.status_code == 401


# ---------------------------------------------------------------------------
# Compliance validation
# ---------------------------------------------------------------------------
class TestComplianceValidate:
    def test_valid_product_returns_200(self, client, auth_headers, sample_product):
        payload = {"product": sample_product, "extractedText": ""}
        res = client.post(
            "/api/compliance/validate",
            data=json.dumps(payload),
            headers=auth_headers,
        )
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert "report" in data
        assert data["report"]["complianceScore"] == 100.0

    def test_missing_product_field_returns_400(self, client, auth_headers):
        res = client.post(
            "/api/compliance/validate",
            data=json.dumps({}),
            headers=auth_headers,
        )
        assert res.status_code == 400

    def test_non_compliant_product(self, client, auth_headers):
        bad_product = {"id": "p1", "name": "Bad Product"}
        payload = {"product": bad_product}
        res = client.post(
            "/api/compliance/validate",
            data=json.dumps(payload),
            headers=auth_headers,
        )
        assert res.status_code == 200
        data = res.get_json()
        assert data["report"]["complianceScore"] < 100.0
        assert data["report"]["isCompliant"] is False


# ---------------------------------------------------------------------------
# OCR extract
# ---------------------------------------------------------------------------
class TestOcrExtract:
    def test_missing_image_returns_400(self, client, auth_headers):
        res = client.post(
            "/api/ocr/extract",
            data=json.dumps({}),
            headers=auth_headers,
        )
        assert res.status_code == 400

    def test_valid_image_returns_200(self, client, auth_headers):
        import base64
        from PIL import Image
        import io

        img = Image.new("RGB", (50, 50), color=(255, 255, 255))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()

        payload = {"imageBase64": b64, "source": "mobile"}
        res = client.post(
            "/api/ocr/extract",
            data=json.dumps(payload),
            headers=auth_headers,
        )
        assert res.status_code == 200
        data = res.get_json()
        assert "extractedText" in data
        assert "confidence" in data
        assert "structuredData" in data


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------
class TestReports:
    def test_get_nonexistent_report_returns_404(self, client, auth_headers):
        res = client.get("/api/reports/nonexistent-id", headers=auth_headers)
        assert res.status_code == 404

    def test_get_user_reports_returns_list(self, client, auth_headers):
        res = client.get("/api/reports/user/uid-123", headers=auth_headers)
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)

    def test_get_inspector_reports_returns_list(self, client, auth_headers):
        res = client.get("/api/reports/inspector", headers=auth_headers)
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)

    def test_inspector_reports_filter_by_status(self, client, auth_headers):
        res = client.get(
            "/api/reports/inspector?status=COMPLIANT", headers=auth_headers
        )
        assert res.status_code == 200

    def test_report_saved_and_retrievable(self, client, auth_headers, sample_product):
        # 1. Create a report
        payload = {"product": sample_product, "extractedText": ""}
        res = client.post(
            "/api/compliance/validate",
            data=json.dumps(payload),
            headers=auth_headers,
        )
        assert res.status_code == 200
        report_id = res.get_json()["report"]["id"]

        # 2. Fetch it back
        res2 = client.get(f"/api/reports/{report_id}", headers=auth_headers)
        assert res2.status_code == 200
        fetched = res2.get_json()
        assert fetched["id"] == report_id


# ---------------------------------------------------------------------------
# E-commerce
# ---------------------------------------------------------------------------
class TestEcommerce:
    def test_missing_url_returns_400(self, client, auth_headers):
        res = client.post(
            "/api/ecommerce/scrape",
            data=json.dumps({}),
            headers=auth_headers,
        )
        assert res.status_code == 400


# ---------------------------------------------------------------------------
# IoT
# ---------------------------------------------------------------------------
class TestIoT:
    def test_missing_device_id_returns_400(self, client):
        res = client.post(
            "/api/iot/data",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert res.status_code == 400

    def test_unregistered_device_fails(self, client):
        # Without pre-registering, Firestore stub returns None → not registered
        payload = {"deviceId": "esp32-test-01"}
        res = client.post(
            "/api/iot/data",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is False
        assert "not registered" in data["message"].lower()
