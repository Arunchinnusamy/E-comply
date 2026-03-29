# E-Comply - Quick Reference

## Essential Commands

### Android Development
```bash
# Build debug APK
./gradlew assembleDebug

# Build release APK
./gradlew assembleRelease

# Run tests
./gradlew test

# Clean build
./gradlew clean
```

### Backend Development
```bash
# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py

# Run with auto-reload
FLASK_ENV=development python app.py
```

## Default Test Credentials

Create these users after setup:

### General User
- Email: user@ecomply.com
- Type: GENERAL_USER

### Inspector
- Email: inspector@ecomply.com
- Type: INSPECTOR

## API Endpoints Quick Reference

### Base URL
- Local: `http://localhost:5000`
- Emulator: `http://10.0.2.2:5000`

### Endpoints
- `GET /health` - Health check
- `POST /api/ocr/extract` - Extract text from image
- `POST /api/compliance/validate` - Validate compliance
- `POST /api/ecommerce/scrape` - Scrape e-commerce
- `POST /api/iot/data` - Process IoT data

## Firebase Collections

### users
```json
{
  "id": "string",
  "email": "string",
  "name": "string",
  "userType": "GENERAL_USER | INSPECTOR",
  "phone": "string",
  "createdAt": timestamp
}
```

### products
```json
{
  "id": "string",
  "name": "string",
  "manufacturerName": "string",
  "manufacturerAddress": "string",
  "netQuantity": "string",
  "mrp": "string",
  "manufacturingDate": "string",
  "expiryDate": "string",
  "customerCareDetails": "string",
  "countryOfOrigin": "string",
  "imageUrl": "string",
  "scannedText": "string",
  "source": "MOBILE_SCAN | ECOMMERCE | IOT_DEVICE",
  "scannedBy": "string",
  "scannedAt": timestamp
}
```

### compliance_reports
```json
{
  "id": "string",
  "productId": "string",
  "productName": "string",
  "complianceScore": number,
  "isCompliant": boolean,
  "complianceStatus": "COMPLIANT | NON_COMPLIANT | PARTIAL_COMPLIANT",
  "missingFields": ["string"],
  "violations": [
    {
      "field": "string",
      "description": "string",
      "severity": "LOW | MEDIUM | HIGH | CRITICAL",
      "ruleViolated": "string"
    }
  ],
  "recommendations": ["string"],
  "riskLevel": "LOW | MEDIUM | HIGH | CRITICAL",
  "aiSummary": "string",
  "inspectorId": "string",
  "inspectorNotes": "string",
  "createdAt": timestamp,
  "updatedAt": timestamp
}
```

## Legal Metrology Mandatory Fields

1. ✅ Manufacturer Name
2. ✅ Manufacturer Address (complete with pin code)
3. ✅ Net Quantity (with unit: kg/g/l/ml)
4. ✅ MRP (inclusive of all taxes)
5. ✅ Manufacturing/Packing Date
6. ✅ Customer Care Details (phone/email)
7. ✅ Country of Origin

## Common Issues & Solutions

### App crashes on startup
- Check Firebase configuration
- Verify google-services.json is present
- Rebuild project

### Backend connection failed
- Verify backend is running
- Check IP address/URL
- Test with curl/Postman first

### OCR not extracting text
- Ensure good lighting
- Hold camera steady
- Use high contrast images
- Check Tesseract installation

### Firebase permission denied
- Review Firestore security rules
- Check user authentication status
- Verify user has correct role

## Performance Tips

### Android
- Enable Proguard for release builds
- Optimize images before upload
- Use pagination for large lists
- Cache frequently accessed data

### Backend
- Use image compression
- Implement caching for OCR results
- Use async processing for heavy tasks
- Monitor memory usage

## Monitoring & Debugging

### Android Logs
```bash
adb logcat | grep "E-Comply"
```

### Backend Logs
```bash
# View logs
tail -f app.log

# Filter errors
grep "ERROR" app.log
```

### Firebase Console
- Monitor authentication events
- Check database usage
- Review storage usage
- Set up alerts

## Production Checklist

### Before Deployment
- [ ] Update all API URLs to production
- [ ] Enable Proguard
- [ ] Remove debug logs
- [ ] Test on multiple devices
- [ ] Verify all permissions
- [ ] Test offline scenarios
- [ ] Review security rules
- [ ] Setup error tracking
- [ ] Configure analytics
- [ ] Test payment flows (if any)

### Backend
- [ ] Set DEBUG=False
- [ ] Configure production database
- [ ] Setup SSL certificates
- [ ] Configure CORS properly
- [ ] Setup logging service
- [ ] Configure backups
- [ ] Load test APIs
- [ ] Setup monitoring
- [ ] Document API changes
- [ ] Test all endpoints

## Support Resources

- [Android Documentation](https://developer.android.com)
- [Jetpack Compose](https://developer.android.com/jetpack/compose)
- [Firebase Documentation](https://firebase.google.com/docs)
- [Flask Documentation](https://flask.palletsprojects.com)
- [Legal Metrology Act](https://consumeraffairs.nic.in)

## Project Structure Summary

```
Ecomply/
├── app/                          # Android application
│   └── src/main/java/com/example/e_comply/
│       ├── data/                 # Data layer
│       │   ├── model/           # Data models
│       │   ├── remote/          # API services
│       │   └── repository/      # Repositories
│       ├── di/                  # Dependency injection
│       ├── ui/                  # UI layer
│       │   ├── navigation/      # Navigation
│       │   ├── screens/         # Compose screens
│       │   ├── theme/           # App theme
│       │   └── viewmodel/       # ViewModels
│       ├── utils/               # Utilities
│       ├── EcomplyApplication.kt
│       └── MainActivity.kt
└── backend/                      # Python backend
    ├── services/                # Business logic
    │   ├── ocr_service.py
    │   ├── compliance_service.py
    │   ├── ecommerce_service.py
    │   └── iot_service.py
    ├── app.py                   # Main Flask app
    ├── config.py                # Configuration
    └── requirements.txt         # Dependencies
```

---

**Last Updated**: February 2026
**Version**: 1.0.0
