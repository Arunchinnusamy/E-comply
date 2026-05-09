"""
test_ocr_service.py
-------------------
Unit tests for OCRService – avoids GPU / heavy model loading
by monkeypatching the easyocr Reader.
"""

import base64
import sys
import types
import pytest
import numpy as np
from PIL import Image
import io


# ---------------------------------------------------------------------------
# Patch easyocr before importing the service
# ---------------------------------------------------------------------------
def _make_easyocr_stub():
    easyocr = types.ModuleType("easyocr")

    class _FakeReader:
        def __init__(self, langs, gpu=False):
            pass

        def readtext(self, image):
            # Always return one fake detection
            return [([[0, 0], [100, 0], [100, 20], [0, 20]], "MRP Rs. 50", 0.95)]

    easyocr.Reader = _FakeReader
    sys.modules["easyocr"] = easyocr
    return easyocr


_make_easyocr_stub()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _make_white_image_b64(w=100, h=100):
    """Return a base64-encoded white PNG image."""
    img = Image.new("RGB", (w, h), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


@pytest.fixture
def service():
    for mod in list(sys.modules.keys()):
        if mod.startswith("services.ocr"):
            del sys.modules[mod]
    from services.ocr_service import OCRService
    return OCRService()


# ---------------------------------------------------------------------------
# Tests – extract_structured_data (pure text parsing, no image needed)
# ---------------------------------------------------------------------------
class TestExtractStructuredData:
    def test_extract_mrp(self, service):
        data = service.extract_structured_data("MRP Rs. 50")
        assert data.get("mrp") == "50"

    def test_extract_rupee_symbol(self, service):
        data = service.extract_structured_data("₹ 99")
        assert data.get("mrp") == "99"

    def test_extract_net_quantity(self, service):
        data = service.extract_structured_data("Net Qty: 500g")
        assert "500g" in data.get("netQuantity", "")

    def test_extract_manufacturing_date(self, service):
        text = "Mfg Date: 01/06/2024"
        data = service.extract_structured_data(text)
        assert "2024" in data.get("manufacturingDate", "")

    def test_extract_country_of_origin(self, service):
        data = service.extract_structured_data("Country of Origin: India")
        assert "India" in data.get("countryOfOrigin", "")

    def test_extract_phone_number(self, service):
        data = service.extract_structured_data("Call us: 9876543210")
        assert data.get("customerCare") is not None

    def test_extract_email(self, service):
        data = service.extract_structured_data("Email: care@brand.com")
        assert "care@brand.com" in data.get("customerCare", "")

    def test_empty_text_returns_empty_dict(self, service):
        data = service.extract_structured_data("")
        assert data == {}


# ---------------------------------------------------------------------------
# Tests – preprocess_image (sanity check only, no assertion on pixel values)
# ---------------------------------------------------------------------------
class TestPreprocessImage:
    def test_preprocess_returns_ndarray(self, service):
        import cv2
        img = np.ones((100, 100, 3), dtype=np.uint8) * 200
        result = service.preprocess_image(img)
        assert result is not None
        assert len(result.shape) == 2  # grayscale output


# ---------------------------------------------------------------------------
# Tests – extract_text_from_base64
# ---------------------------------------------------------------------------
class TestExtractFromBase64:
    def test_returns_dict_with_keys(self, service):
        b64 = _make_white_image_b64()
        result = service.extract_text_from_base64(b64, source="mobile")
        assert "text" in result
        assert "confidence" in result
        assert "structured_data" in result

    def test_confidence_between_0_and_1(self, service):
        b64 = _make_white_image_b64()
        result = service.extract_text_from_base64(b64)
        assert 0.0 <= result["confidence"] <= 1.0

    def test_invalid_base64_raises(self, service):
        with pytest.raises(Exception):
            service.extract_text_from_base64("NOT_VALID_BASE64!!!")
