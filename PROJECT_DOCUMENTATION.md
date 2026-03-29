# E-Comply - AI-Based Legal Metrology Compliance System

## Project Overview

E-Comply is an intelligent automated compliance checking system that validates packaged products according to Indian Legal Metrology rules. The system integrates a mobile application, backend AI engine, open-source e-commerce data access, and IoT hardware to perform real-time compliance verification and automated report generation.

## System Architecture

```
┌─────────────────┐
│  Mobile App     │
│  (Android)      │
└────────┬────────┘
         │
         ├──── Camera Scanner (OCR)
         ├──── User Authentication
         ├──── Compliance Reports
         └──── Inspector Dashboard
         │
         ▼
┌─────────────────────────────────┐
│    Python Backend (Flask)       │
│                                 │
│  ┌──────────────────────────┐  │
│  │  OCR Service             │  │
│  │  - Tesseract/EasyOCR     │  │
│  └──────────────────────────┘  │
│                                 │
│  ┌──────────────────────────┐  │
│  │  Compliance Engine       │  │
│  │  - Rule Validation       │  │
│  │  - AI Analysis           │  │
│  └──────────────────────────┘  │
│                                 │
│  ┌──────────────────────────┐  │
│  │  E-commerce Integration  │  │
│  │  - Web Scraping          │  │
│  │  - API Integration       │  │
│  └──────────────────────────┘  │
│                                 │
│  ┌──────────────────────────┐  │
│  │  IoT Integration         │  │
│  │  - ESP32 Support         │  │
│  └──────────────────────────┘  │
└────────────┬────────────────────┘
             │
             ▼
     ┌──────────────┐
     │   Firebase   │
     │              │
     │ - Auth       │
     │ - Firestore  │
     │ - Storage    │
     └──────────────┘
```

## Features

### Mobile Application (Android)
- **User Types**: General users and inspectors
- **Camera Scanner**: Capture product labels and extract text using OCR
- **Compliance Validation**: Real-time validation against Legal Metrology rules
- **Compliance Reports**: Detailed reports with scores, violations, and recommendations
- **Inspector Dashboard**: Analytics and report management for inspectors
- **Firebase Authentication**: Secure user authentication
- **Firebase Storage**: Store product images
- **Firebase Firestore**: Real-time database for products and reports

### Backend Services (Python)
- **OCR Processing**: Tesseract and EasyOCR for text extraction
- **AI Compliance Engine**: Rule-based validation with intelligent analysis
- **E-commerce Integration**: Scrape product data from Amazon, Flipkart, etc.
- **IoT Support**: Process data from ESP32 devices
- **Automated Reporting**: Generate comprehensive compliance reports
- **REST APIs**: Clean API endpoints for mobile integration

### Legal Metrology Compliance Checking
All checks are based on the Legal Metrology (Packaged Commodities) Rules, 2011:

1. **Manufacturer Name** - Mandatory
2. **Manufacturer Address** - Complete address with pin code
3. **Net Quantity** - With standard units (kg, g, l, ml)
4. **MRP** - Maximum Retail Price inclusive of taxes
5. **Manufacturing/Packing Date** - Month and year
6. **Customer Care Details** - Phone or email
7. **Country of Origin** - For imported goods
8. **Expiry Date** - For applicable products
9. **Batch Number** - For traceability (recommended)

## Technology Stack

### Android App
- **Language**: Kotlin
- **UI Framework**: Jetpack Compose
- **Architecture**: MVVM with Repository Pattern
- **Dependency Injection**: Hilt
- **Networking**: Retrofit + OkHttp
- **Camera**: CameraX
- **OCR**: ML Kit Text Recognition
- **Image Loading**: Coil
- **Authentication**: Firebase Auth
- **Database**: Firebase Firestore
- **Storage**: Firebase Storage

### Backend
- **Language**: Python 3.8+
- **Framework**: Flask
- **OCR**: Tesseract OCR, EasyOCR
- **Image Processing**: OpenCV, Pillow
- **AI/NLP**: spaCy, NLTK
- **Web Scraping**: BeautifulSoup4, Selenium
- **Database**: Firebase Admin SDK

## Setup Instructions

### Prerequisites
1. Android Studio (latest version)
2. Python 3.8 or higher
3. Firebase project with Auth, Firestore, and Storage enabled
4. Tesseract OCR installed on backend server

### Android App Setup

1. **Clone the repository**
```bash
cd c:\Users\shiva\AndroidStudioProjects\Ecomply
```

2. **Add Firebase Configuration**
   - Download `google-services.json` from Firebase Console
   - Place it in `app/` directory

3. **Update Backend URL**
   - Edit `RetrofitClient.kt`
   - Change BASE_URL to your backend server address

4. **Build the project**
   - Open project in Android Studio
   - Sync Gradle files
   - Build and run on device/emulator

### Backend Setup

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
   - Create `.env` file
   - Add Firebase credentials path
   - Configure Tesseract path if needed

5. **Run the server**
```bash
python app.py
```

Server will start on `http://localhost:5000`

### IoT Device Setup (ESP32)

1. **Hardware Requirements**
   - ESP32 board
   - Camera module (OV2640 or similar)
   - Optional: DHT22 sensor for temperature/humidity

2. **Configuration**
   - Upload Arduino sketch to ESP32
   - Configure WiFi credentials
   - Set backend server endpoint

3. **API Integration**
   - Device sends images to `/api/iot/data`
   - Include device ID for identification
   - Optionally include sensor readings

## API Documentation

### OCR Endpoint
```
POST /api/ocr/extract
Content-Type: application/json

{
  "imageBase64": "base64_encoded_image",
  "source": "mobile"
}
```

### Compliance Validation
```
POST /api/compliance/validate
Content-Type: application/json

{
  "product": {
    "name": "Product Name",
    "manufacturerName": "Manufacturer",
    ...
  },
  "extractedText": "OCR extracted text"
}
```

### E-commerce Scraping
```
POST /api/ecommerce/scrape
Content-Type: application/json

{
  "url": "product_url",
  "platform": "amazon"
}
```

### IoT Data Processing
```
POST /api/iot/data
Content-Type: application/json

{
  "deviceId": "ESP32_001",
  "imageBase64": "base64_image",
  "sensorData": {
    "temperature": 25.5,
    "humidity": 60
  }
}
```

## User Roles

### General User
- Scan product labels
- View compliance reports
- Access scan history
- Get compliance recommendations

### Inspector
- Access all compliance reports
- View analytics dashboard
- Filter reports by status/risk
- Export reports for audit
- Add inspector notes

## Compliance Scoring

The system calculates compliance scores based on:
- **Mandatory Fields**: 100% weight for all mandatory fields
- **Format Validation**: Penalties for incorrect formats
- **Risk Assessment**: Critical, High, Medium, Low

## Risk Levels

- **CRITICAL**: Compliance score < 50% or critical violations
- **HIGH**: Compliance score < 70% or high-severity violations
- **MEDIUM**: Compliance score < 90%
- **LOW**: Compliance score >= 90%

## Future Enhancements

1. **AI Improvements**
   - Deep learning models for better OCR
   - NLP for context understanding
   - Predictive compliance analysis

2. **Additional Features**
   - Barcode scanning
   - QR code integration
   - Multilingual support
   - Offline mode

3. **Integrations**
   - More e-commerce platforms
   - Government compliance databases
   - Third-party audit systems

4. **Mobile Enhancements**
   - Batch scanning
   - Voice commands
   - AR overlay for scanning guidance

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions:
- GitHub Issues: [Repository URL]
- Email: support@ecomply.com

## Credits

Developed as an intelligent RegTech solution for automating Legal Metrology compliance verification in India.

---

**Note**: This system is designed to assist with compliance checking but does not replace official inspections or legal advice. Always consult with legal experts for regulatory compliance.
