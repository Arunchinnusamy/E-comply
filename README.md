# E-Comply - AI-Based Legal Metrology Compliance System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Android](https://img.shields.io/badge/Platform-Android-green.svg)](https://developer.android.com)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![Firebase](https://img.shields.io/badge/Backend-Firebase-orange.svg)](https://firebase.google.com)

An intelligent automated compliance checking system that validates packaged products according to Indian Legal Metrology rules using AI, OCR, and IoT integration.

## 🌟 Features

### Mobile Application
- 📱 **User & Inspector Roles** - Dual interface for general users and legal metrology inspectors
- 📸 **Smart Camera Scanner** - Capture product labels with intelligent text extraction
- 🤖 **AI-Powered OCR** - Extract product information using ML Kit and backend AI
- ✅ **Real-time Compliance Validation** - Instant analysis against Legal Metrology rules
- 📊 **Comprehensive Reports** - Detailed compliance scores, violations, and recommendations
- 👨‍💼 **Inspector Dashboard** - Analytics, statistics, and report management
- 🔥 **Firebase Integration** - Secure authentication and cloud storage

### Backend Services
- 🔍 **Advanced OCR Processing** - Tesseract and EasyOCR for accurate text extraction
- 🧠 **AI Compliance Engine** - Rule-based validation with intelligent analysis
- 🛒 **E-commerce Integration** - Scrape and validate products from Amazon, Flipkart
- 🌐 **IoT Support** - Process data from ESP32 devices with camera modules
- 📝 **Automated Reporting** - Generate AI-powered compliance summaries
- 🔌 **RESTful APIs** - Clean and documented API endpoints

## 🏗️ Architecture

```
┌─────────────┐
│ Android App │ ──> Camera + OCR
└──────┬──────┘     Firebase Auth
       │            Firestore DB
       ▼
┌─────────────┐
│ Python API  │ ──> OCR Service
│   (Flask)   │     Compliance Engine
└──────┬──────┘     E-commerce Scraper
       │            IoT Integration
       ▼
┌─────────────┐
│  Firebase   │
│  Database   │
└─────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Android Studio (latest version)
- Python 3.8+
- Firebase account
- Tesseract OCR

### Setup in 5 Minutes

1. **Clone the repository**
```bash
git clone <repository-url>
cd Ecomply
```

2. **Setup Firebase** (See [SETUP_GUIDE.md](SETUP_GUIDE.md))
   - Create Firebase project
   - Enable Auth, Firestore, Storage
   - Download `google-services.json` → place in `app/`

3. **Setup Android App**
```bash
# Open in Android Studio
# Sync Gradle
# Build and Run
```

4. **Setup Backend**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python app.py
```

5. **Start Developing! 🎉**

## 📱 Screenshots

| Home Screen | Scanner | Compliance Report | Inspector Dashboard |
|------------|---------|-------------------|-------------------|
| ![Home](screenshots/home.png) | ![Scanner](screenshots/scanner.png) | ![Report](screenshots/report.png) | ![Dashboard](screenshots/dashboard.png) |

## 🛠️ Technology Stack

### Android
- **Language**: Kotlin
- **UI**: Jetpack Compose
- **Architecture**: MVVM + Repository Pattern
- **DI**: Hilt/Dagger
- **Networking**: Retrofit + OkHttp
- **Camera**: CameraX
- **OCR**: ML Kit Text Recognition
- **Firebase**: Auth, Firestore, Storage

### Backend
- **Language**: Python 3.8+
- **Framework**: Flask
- **OCR**: Tesseract, EasyOCR
- **Image Processing**: OpenCV, Pillow
- **AI/ML**: spaCy, NLTK, scikit-learn
- **Web Scraping**: BeautifulSoup4, Selenium
- **Database**: Firebase Admin SDK

## 📋 Legal Metrology Compliance

The system validates products against **Legal Metrology (Packaged Commodities) Rules, 2011**:

✅ **Mandatory Fields:**
1. Manufacturer Name
2. Manufacturer Address
3. Net Quantity (with units)
4. MRP (Maximum Retail Price)
5. Manufacturing/Packing Date
6. Customer Care Details
7. Country of Origin

**Compliance Scoring:**
- 100% = Fully Compliant ✅
- 70-99% = Partially Compliant ⚠️
- < 70% = Non-Compliant ❌

**Risk Levels:**
- 🟢 LOW: Score ≥ 90%
- 🟡 MEDIUM: Score 70-89%
- 🟠 HIGH: Score 50-69%
- 🔴 CRITICAL: Score < 50%

## 📖 Documentation

- [**Project Documentation**](PROJECT_DOCUMENTATION.md) - Complete system overview
- [**Setup Guide**](SETUP_GUIDE.md) - Detailed setup instructions
- [**Quick Reference**](QUICK_REFERENCE.md) - Commands and API reference
- [**Backend README**](backend/README.md) - Backend API documentation

## 🔌 API Endpoints

### Base URL
```
Local: http://localhost:5000
Emulator: http://10.0.2.2:5000
```

### Key Endpoints
```http
POST /api/ocr/extract          # Extract text from image
POST /api/compliance/validate  # Validate product compliance
POST /api/ecommerce/scrape     # Scrape e-commerce product
POST /api/iot/data             # Process IoT device data
GET  /api/reports/{id}         # Get compliance report
```

See [API Documentation](backend/README.md) for complete reference.

## 🎯 Use Cases

### For Consumers
- Verify product labeling before purchase
- Check compliance with Legal Metrology standards
- Make informed purchasing decisions
- Report non-compliant products

### For Inspectors
- Streamline compliance inspections
- Access centralized reports database
- Identify high-risk products quickly
- Generate audit-ready reports

### For Manufacturers
- Self-audit product labels
- Ensure regulatory compliance
- Reduce risk of penalties
- Improve product labeling

### For E-commerce Platforms
- Validate product listings
- Ensure marketplace compliance
- Automate quality checks
- Reduce customer complaints

## 🤖 IoT Integration

### ESP32 Device Setup
```cpp
// Connect ESP32 with camera module
// Configure WiFi credentials
// Set backend API endpoint
// Capture and send product images
```

### Supported Features
- Automatic product scanning
- Image capture and transmission
- Temperature/humidity monitoring
- Real-time compliance alerts

## 🧪 Testing

### Android Tests
```bash
./gradlew test
./gradlew connectedAndroidTest
```

### Backend Tests
```bash
pytest tests/
```

## 📦 Deployment

### Android (Play Store)
1. Generate signed APK/Bundle
2. Update version code
3. Test on multiple devices
4. Upload to Google Play Console

### Backend (Cloud)
```bash
# Heroku deployment example
heroku create ecomply-backend
git push heroku main
```

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed deployment instructions.

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

Developed as an intelligent RegTech solution for automating Legal Metrology compliance verification.

## 🙏 Acknowledgments

- Indian Legal Metrology Department
- Firebase team for cloud infrastructure
- Open-source OCR communities
- Android and Python communities

## 📧 Contact

For questions, issues, or suggestions:
- **Email**: support@ecomply.com
- **GitHub Issues**: [Create an issue](../../issues)

## ⚠️ Disclaimer

This system is designed to assist with compliance checking but does not replace official inspections or legal advice. Always consult with legal experts and official authorities for regulatory compliance matters.

---

**Made with ❤️ for Legal Metrology Compliance**

**Version**: 1.0.0 | **Last Updated**: February 2026
