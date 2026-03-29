# AI-Based Legal Metrology Compliance Checking System - Backend

## Overview
This is the Python backend for the E-Comply mobile application. It provides REST APIs for OCR processing, compliance validation, e-commerce integration, and IoT device data processing.

## Features
- OCR text extraction from images
- AI-based Legal Metrology compliance validation
- E-commerce platform integration (Flipkart, Amazon)
- IoT device (ESP32) data processing
- Automated report generation
- Firebase integration

## Tech Stack
- **Framework**: Flask
- **OCR**: Tesseract OCR, EasyOCR
- **AI/ML**: spaCy, NLTK, scikit-learn
- **Web Scraping**: BeautifulSoup4, Selenium
- **Database**: Firebase Admin SDK
- **Image Processing**: OpenCV, Pillow

## Installation

### Prerequisites
- Python 3.8+
- Tesseract OCR installed
- Firebase Admin SDK credentials

### Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
Create a `.env` file with:
```
FIREBASE_CREDENTIALS_PATH=path/to/firebase-credentials.json
```

4. Run the server:
```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### OCR
- `POST /api/ocr/extract` - Extract text from product image

### Compliance
- `POST /api/compliance/validate` - Validate product compliance
- `GET /api/reports/{reportId}` - Get compliance report
- `GET /api/reports/user/{userId}` - Get user reports
- `GET /api/reports/inspector` - Get all reports for inspectors

### E-commerce
- `POST /api/ecommerce/scrape` - Scrape product from e-commerce platform

### IoT
- `POST /api/iot/data` - Process IoT device data

## Project Structure
```
backend/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── config.py             # Configuration settings
├── models/               # Data models
├── services/             # Business logic services
│   ├── ocr_service.py
│   ├── compliance_service.py
│   ├── ecommerce_service.py
│   └── iot_service.py
├── utils/                # Utility functions
├── routes/               # API routes
└── tests/                # Unit tests
```

## License
MIT
