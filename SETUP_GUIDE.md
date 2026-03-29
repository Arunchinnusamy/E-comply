# E-Comply Setup and Configuration Guide

## Quick Start Guide

### 1. Firebase Setup

#### Create Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project named "E-Comply"
3. Enable Google Analytics (optional)

#### Enable Authentication
1. Go to Authentication → Sign-in method
2. Enable "Email/Password" provider
3. Optional: Enable Google Sign-in

#### Setup Firestore Database
1. Go to Firestore Database
2. Create database in production mode
3. Add indexes:
   ```
   Collection: compliance_reports
   Fields: createdAt (Descending), complianceStatus (Ascending)
   
   Collection: products
   Fields: scannedBy (Ascending), scannedAt (Descending)
   ```

#### Setup Storage
1. Go to Storage
2. Create default bucket
3. Update storage rules:
   ```
   rules_version = '2';
   service firebase.storage {
     match /b/{bucket}/o {
       match /product_images/{imageId} {
         allow read: if request.auth != null;
         allow write: if request.auth != null && request.resource.size < 10 * 1024 * 1024;
       }
     }
   }
   ```

#### Update Firestore Security Rules
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    match /products/{productId} {
      allow read: if request.auth != null;
      allow create: if request.auth != null;
      allow update, delete: if request.auth != null && 
        resource.data.scannedBy == request.auth.uid;
    }
    
    match /compliance_reports/{reportId} {
      allow read: if request.auth != null;
      allow create: if request.auth != null;
      allow update: if request.auth != null && 
        (resource.data.inspectorId == request.auth.uid ||
         get(/databases/$(database)/documents/users/$(request.auth.uid)).data.userType == 'INSPECTOR');
    }
  }
}
```

#### Download Configuration Files
1. For Android:
   - Project Settings → General
   - Download `google-services.json`
   - Place in `app/` directory

2. For Backend:
   - Project Settings → Service Accounts
   - Generate new private key
   - Save as `firebase-credentials.json` in `backend/` directory

### 2. Android App Configuration

#### Update Firebase Configuration
File: `app/google-services.json`
- Ensure this file is in the `app/` directory
- Add to `.gitignore` to prevent committing

#### Update Backend URL
File: `app/src/main/java/com/example/e_comply/data/remote/RetrofitClient.kt`

```kotlin
// For Android Emulator connecting to local backend
private const val BASE_URL = "http://10.0.2.2:5000/"

// For Physical Device (replace with your computer's IP)
private const val BASE_URL = "http://192.168.1.100:5000/"

// For Production
private const val BASE_URL = "https://your-backend-domain.com/"
```

#### Build Configuration
File: `app/build.gradle.kts`

No changes needed - dependencies are already configured.

#### Camera Permissions
Permissions are already added in `AndroidManifest.xml`

### 3. Backend Configuration

#### Install Python Dependencies
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

#### Install Tesseract OCR

**Windows:**
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to `C:\Program Files\Tesseract-OCR`
3. Add to system PATH

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install libtesseract-dev
```

**MacOS:**
```bash
brew install tesseract
```

#### Configure Environment Variables
Create `backend/.env` file:

```env
# Flask Configuration
DEBUG=True
HOST=0.0.0.0
PORT=5000

# Firebase Configuration
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json

# OCR Configuration
TESSERACT_CMD=tesseract
USE_EASYOCR=True

# Server Configuration
MAX_CONTENT_LENGTH=16777216
```

#### Place Firebase Credentials
- Copy `firebase-credentials.json` to `backend/` directory
- Add to `.gitignore`

#### Run Backend Server
```bash
cd backend
python app.py
```

Server will start on `http://localhost:5000`

### 4. Testing the Setup

#### Test Backend Health
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "E-Comply Backend is running"
}
```

#### Test in Android App
1. Build and run the app
2. Create a test account (Sign Up)
3. Log in
4. Try scanning a product label
5. View the compliance report

### 5. Network Configuration

#### For Emulator
- Backend URL: `http://10.0.2.2:5000/`
- No additional configuration needed

#### For Physical Device
1. Ensure phone and computer are on same WiFi network
2. Find computer's IP address:
   - Windows: `ipconfig`
   - Linux/Mac: `ifconfig` or `ip addr`
3. Update `BASE_URL` in `RetrofitClient.kt`
4. Update `AndroidManifest.xml` if needed (already configured)

#### Firewall Configuration
If connection fails, allow Python through firewall:

**Windows:**
- Windows Defender Firewall → Allow an app
- Add Python to allowed apps

**Linux:**
```bash
sudo ufw allow 5000/tcp
```

### 6. Production Deployment

#### Backend Deployment (Heroku Example)
```bash
# Install Heroku CLI
heroku login

# Create app
heroku create ecomply-backend

# Add buildpack for Python
heroku buildpacks:add heroku/python

# Deploy
git push heroku main

# Set environment variables
heroku config:set FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
```

#### Android App (Play Store)
1. Generate signed APK/Bundle
2. Increment version code
3. Update `BASE_URL` to production
4. Test thoroughly
5. Upload to Play Console

### 7. ESP32 IoT Device Setup

#### Arduino Code Sketch
```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include "esp_camera.h"
#include "base64.h"

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Backend server
const char* serverUrl = "http://YOUR_SERVER_IP:5000/api/iot/data";
const char* deviceId = "ESP32_001";

void setup() {
  Serial.begin(115200);
  
  // Initialize WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  
  // Initialize camera
  camera_config_t config;
  // ... camera configuration
  esp_camera_init(&config);
}

void loop() {
  // Capture image
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    return;
  }
  
  // Convert to base64
  String imageBase64 = base64::encode(fb->buf, fb->len);
  
  // Send to backend
  if(WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    
    String jsonPayload = "{";
    jsonPayload += "\"deviceId\":\"" + String(deviceId) + "\",";
    jsonPayload += "\"imageBase64\":\"" + imageBase64 + "\",";
    jsonPayload += "\"sensorData\":{\"temperature\":25.5}";
    jsonPayload += "}";
    
    int httpResponseCode = http.POST(jsonPayload);
    Serial.println(httpResponseCode);
    
    http.end();
  }
  
  esp_camera_fb_return(fb);
  delay(30000); // Scan every 30 seconds
}
```

### 8. Troubleshooting

#### App won't connect to backend
- Check URL in RetrofitClient.kt
- Verify backend is running
- Check firewall settings
- For emulator, use `10.0.2.2`
- For device, use computer's IP

#### Firebase Authentication fails
- Verify `google-services.json` is in app directory
- Check Firebase console for enabled auth methods
- Rebuild project after adding firebase file

#### OCR not working
- Check Tesseract installation
- Verify TESSERACT_CMD in .env
- Test with `tesseract --version`
- Try enabling EasyOCR as fallback

#### Camera not working
- Grant camera permission in app settings
- Check device compatibility
- Ensure camera hardware is available

#### Backend crashes on image processing
- Check image size (max 16MB)
- Verify OpenCV installation
- Check available memory
- Review logs for specific errors

### 9. Development Tips

#### Enable Debug Logging
Android: Already enabled in debug builds

Backend:
```python
# In app.py, set DEBUG=True
app.config['DEBUG'] = True
```

#### Test APIs with Postman
Import the collection:
- Base URL: `http://localhost:5000`
- Add sample requests for all endpoints

#### Database Inspection
- Firebase Console → Firestore Database
- View documents and collections
- Test queries directly

### 10. Maintenance

#### Update Dependencies
Android:
```bash
# Check for updates in Android Studio
Tools → SDK Manager
```

Backend:
```bash
pip list --outdated
pip install --upgrade package_name
```

#### Monitor Firebase Usage
- Firebase Console → Usage and billing
- Set budget alerts
- Monitor quota limits

#### Backup Database
- Firestore → Export data
- Schedule regular backups
- Store in Google Cloud Storage

---

For additional help, refer to:
- [Firebase Documentation](https://firebase.google.com/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Android Developers](https://developer.android.com/)
