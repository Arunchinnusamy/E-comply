import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration settings for the application"""
    
    # Flask settings
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # Firebase settings
    FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')

    # IoT settings
    # Set IOT_API_KEY in .env – leave blank to skip key check (dev/debug only)
    IOT_API_KEY = os.getenv('IOT_API_KEY', '')
    
    # OCR settings
    TESSERACT_CMD = os.getenv('TESSERACT_CMD', 'tesseract')  # Path to tesseract executable
    USE_EASYOCR = os.getenv('USE_EASYOCR', 'True') == 'True'

    # ── AI / ML Model Settings ────────────────────────────────────────
    # Gemini API — set your key in .env: GEMINI_API_KEY=AIza...
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    USE_GEMINI = os.getenv('USE_GEMINI', 'True') == 'True'

    # ML Risk Prediction — uses trained Random Forest model
    USE_ML_RISK = os.getenv('USE_ML_RISK', 'True') == 'True'
    
    # Legal Metrology Rules — all 16 mandatory fields
    MANDATORY_FIELDS = [
        'Product Name',
        'Brand Name',
        'Category',
        'Manufacturer Name',
        'Manufacturer Address',
        'Importer Name',
        'Importer Address',
        'MRP',
        'Net Quantity',
        'Manufacturing/Packing Date',
        'Expiry Date',
        'Batch Number',
        'Customer Care Details',
        'Country of Origin',
        'Barcode / QR Code',
        'License Number',
    ]
    
    # E-commerce settings
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    
    # Upload settings
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    @staticmethod
    def init_app(app):
        """Initialize application configuration"""
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
