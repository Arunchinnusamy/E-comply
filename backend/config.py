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
    
    # OCR settings
    TESSERACT_CMD = os.getenv('TESSERACT_CMD', 'tesseract')  # Path to tesseract executable
    USE_EASYOCR = os.getenv('USE_EASYOCR', 'True') == 'True'
    
    # Legal Metrology Rules
    MANDATORY_FIELDS = [
        'Manufacturer Name',
        'Manufacturer Address',
        'Net Quantity',
        'MRP',
        'Manufacturing/Packing Date',
        'Customer Care Details',
        'Country of Origin'
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
