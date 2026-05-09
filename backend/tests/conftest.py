"""
conftest.py
-----------
Shared pytest fixtures for the E-Comply backend test suite.

Stubs every heavy / optional dependency so the test suite runs without
installing OpenCV, Tesseract, EasyOCR, BeautifulSoup, Selenium, or GPU libs.
All Firebase / Firestore calls are intercepted by an in-memory stub.
"""

import sys
import types
import pytest


# ---------------------------------------------------------------------------
# Stub heavy optional dependencies BEFORE any app code is imported
# ---------------------------------------------------------------------------

def _stub_module(name: str, **attrs):
    """Register a minimal stub module under ``name``."""
    mod = types.ModuleType(name)
    for k, v in attrs.items():
        setattr(mod, k, v)
    sys.modules[name] = mod
    return mod


# ── numpy ──────────────────────────────────────────────────────────────────
import numpy as _real_np  # noqa: E402 – numpy is a lightweight dep usually present
# If numpy isn't installed, stub it too
if "numpy" not in sys.modules:
    _stub_module("numpy")

# ── PIL / Pillow ───────────────────────────────────────────────────────────
try:
    from PIL import Image as _PIL_Image  # noqa: F401
except ImportError:
    _pil = _stub_module("PIL")
    _img_mod = _stub_module("PIL.Image")
    _pil.Image = _img_mod

# ── cv2 (OpenCV) ───────────────────────────────────────────────────────────
if "cv2" not in sys.modules:
    import numpy as np

    _cv2 = _stub_module(
        "cv2",
        COLOR_RGB2BGR=4,
        COLOR_BGR2GRAY=6,
        ADAPTIVE_THRESH_GAUSSIAN_C=1,
        THRESH_BINARY=0,
    )

    def _cvtColor(img, code):  # noqa: N802
        # Return a 2-D grayscale-like array regardless of input
        if img.ndim == 3:
            return img.mean(axis=2).astype(np.uint8)
        return img

    def _fastNlMeansDenoising(img, *a, **kw):
        return img

    def _adaptiveThreshold(img, *a, **kw):
        return img

    def _dilate(img, *a, **kw):
        return img

    def _erode(img, *a, **kw):
        return img

    _cv2.cvtColor = _cvtColor
    _cv2.fastNlMeansDenoising = _fastNlMeansDenoising
    _cv2.adaptiveThreshold = _adaptiveThreshold
    _cv2.dilate = _dilate
    _cv2.erode = _erode
    _cv2.ones = np.ones

# ── pytesseract ────────────────────────────────────────────────────────────
if "pytesseract" not in sys.modules:
    _tess = _stub_module("pytesseract")
    _tess.image_to_string = lambda img, *a, **kw: "MRP Rs. 50\n200g\nIndia"
    _output = types.SimpleNamespace(DICT="dict")
    _tess.Output = _output
    _tess.image_to_data = lambda img, *a, **kw: {"conf": ["95", "90"], "text": ["MRP", "50"]}

# ── easyocr ────────────────────────────────────────────────────────────────
if "easyocr" not in sys.modules:
    _easyocr = _stub_module("easyocr")

    class _FakeEasyOCRReader:
        def __init__(self, langs, gpu=False):
            pass
        def readtext(self, image):
            return [([[0, 0], [100, 0], [100, 20], [0, 20]], "MRP Rs. 50", 0.95)]

    _easyocr.Reader = _FakeEasyOCRReader

# ── beautifulsoup4 (bs4) ───────────────────────────────────────────────────
if "bs4" not in sys.modules:
    _bs4 = _stub_module("bs4")

    class _FakeSoup:
        def __init__(self, content, parser):
            self._text = content.decode("utf-8", errors="ignore") if isinstance(content, bytes) else str(content)
        def find(self, *a, **kw):
            return None
        def find_all(self, *a, **kw):
            return []
        def get_text(self):
            return self._text

    _bs4.BeautifulSoup = _FakeSoup

# ── selenium ───────────────────────────────────────────────────────────────
for _sel_mod in ["selenium", "selenium.webdriver", "selenium.webdriver.chrome",
                  "selenium.webdriver.chrome.options",
                  "selenium.webdriver.chrome.service"]:
    if _sel_mod not in sys.modules:
        _stub_module(_sel_mod)


# ---------------------------------------------------------------------------
# Stub firebase_admin before any app module is imported so tests never try
# to connect to Firebase.
# ---------------------------------------------------------------------------
def _make_firebase_stub():
    """Create minimal in-memory firebase_admin stub."""
    fb = types.ModuleType("firebase_admin")
    fb._apps = {"[DEFAULT]": object()}       # pretend already initialised

    # credentials sub-module
    creds = types.ModuleType("firebase_admin.credentials")
    creds.Certificate = lambda path: object()
    fb.credentials = creds
    sys.modules["firebase_admin.credentials"] = creds

    # auth sub-module
    auth_mod = types.ModuleType("firebase_admin.auth")

    class _FakeDecoded(dict):
        pass

    def verify_id_token(token):
        if token == "valid-token":
            return {"uid": "test-uid-123", "email": "test@example.com"}
        raise auth_mod.InvalidIdTokenError("bad token")

    auth_mod.verify_id_token = verify_id_token
    auth_mod.ExpiredIdTokenError = type("ExpiredIdTokenError", (Exception,), {})
    auth_mod.RevokedIdTokenError = type("RevokedIdTokenError", (Exception,), {})
    auth_mod.InvalidIdTokenError = type("InvalidIdTokenError", (Exception,), {})
    fb.auth = auth_mod
    sys.modules["firebase_admin.auth"] = auth_mod

    # firestore sub-module
    fs = types.ModuleType("firebase_admin.firestore")

    class _FakeQuery:
        DESCENDING = "DESCENDING"

    fs.client = lambda: _FakeFirestoreClient()
    fs.Query = _FakeQuery
    fb.firestore = fs
    sys.modules["firebase_admin.firestore"] = fs

    fb.initialize_app = lambda *a, **kw: None

    return fb


class _FakeDoc:
    def __init__(self, data=None):
        self._data = data
        self.exists = data is not None

    def to_dict(self):
        return dict(self._data) if self._data else {}


class _FakeCollectionRef:
    """In-memory collection: stores docs in a plain dict."""

    def __init__(self):
        self._docs: dict[str, dict] = {}

    def document(self, doc_id):
        return _FakeDocRef(self._docs, doc_id)

    def where(self, field, op, value):
        return _FakeQuery(self._docs, [(field, op, value)])

    def order_by(self, field, direction=None):
        return _FakeQuery(self._docs, [])

    def limit(self, n):
        return _FakeQuery(self._docs, [], limit=n)

    def stream(self):
        return [_FakeDoc(d) for d in self._docs.values()]


class _FakeDocRef:
    def __init__(self, store, doc_id):
        self._store = store
        self._id = doc_id

    def set(self, data):
        self._store[self._id] = dict(data)

    def get(self):
        return _FakeDoc(self._store.get(self._id))

    def update(self, data):
        if self._id in self._store:
            self._store[self._id].update(data)

    def delete(self):
        self._store.pop(self._id, None)


class _FakeQuery:
    def __init__(self, docs, filters, limit=None):
        self._docs = docs
        self._filters = filters
        self._limit = limit

    def where(self, field, op, value):
        self._filters.append((field, op, value))
        return self

    def order_by(self, field, direction=None):
        return self

    def limit(self, n):
        self._limit = n
        return self

    def stream(self):
        results = []
        for doc in self._docs.values():
            match = True
            for field, op, value in self._filters:
                dv = doc.get(field)
                if op == "==" and dv != value:
                    match = False
                    break
            if match:
                results.append(_FakeDoc(doc))
        if self._limit:
            results = results[: self._limit]
        return results


class _FakeFirestoreClient:
    """One shared store per collection name."""

    def __init__(self):
        self._collections: dict[str, _FakeCollectionRef] = {}

    def collection(self, name):
        if name not in self._collections:
            self._collections[name] = _FakeCollectionRef()
        return self._collections[name]


# ---------------------------------------------------------------------------
# Register the stub before importing anything from the app
# ---------------------------------------------------------------------------
_fb_stub = _make_firebase_stub()
sys.modules["firebase_admin"] = _fb_stub


# ---------------------------------------------------------------------------
# Flask test client fixture
# ---------------------------------------------------------------------------
@pytest.fixture
def client():
    """Return a Flask test client with Firebase fully stubbed out."""
    import importlib, sys

    # Force fresh import of app so stubs are picked up
    for mod in list(sys.modules.keys()):
        if mod.startswith(("app", "services", "config")):
            del sys.modules[mod]

    import app as flask_app

    flask_app.app.config["TESTING"] = True
    with flask_app.app.test_client() as c:
        yield c


@pytest.fixture
def auth_headers():
    """Authorization header carrying the stub's valid token."""
    return {"Authorization": "Bearer valid-token", "Content-Type": "application/json"}


@pytest.fixture
def sample_product():
    """A fully-compliant sample product payload (all 16 mandatory fields)."""
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

