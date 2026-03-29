# Firebase Configuration Guide

## Overview
The `google-services.json` file is essential for Firebase integration in Android. This file contains your Firebase project credentials and configuration.

## How to Get Your google-services.json

### Step 1: Go to Firebase Console
1. Open [Firebase Console](https://console.firebase.google.com/)
2. Click on your existing project or create a new one
3. If you don't have a project, click **"Create a new project"**

### Step 2: Register Your Android App
1. In the Firebase Console, select your project
2. Click the **"Android"** icon to add an Android app
3. Enter the following details:
   - **Package name**: `com.example.e_comply`
   - **App nickname** (optional): `E-Comply`
   - **Debug signing certificate SHA-1** (optional but recommended):
     - Open Android Studio
     - Go to: **Tools → Gradle → :app → android → signingReport**
     - Copy the SHA1 hash from the debug variant
     - Paste it in the Firebase console

### Step 3: Download google-services.json
1. Click **"Register app"**
2. Click **"Download google-services.json"**
3. Move the downloaded file to: `app/google-services.json`

### Step 4: Verify the File Location
Ensure the file is in the correct location:
```
Ecomply/
├── app/
│   ├── google-services.json  ← File should be here
│   ├── build.gradle.kts
│   ├── src/
│   │   ├── main/
│   │   ├── androidTest/
│   │   └── test/
│   └── ...
└── ...
```

## What's in google-services.json

The file contains:
- **Project ID**: Your Firebase project identifier
- **API Keys**: Public keys for web, Android, iOS
- **Firebase-specific configuration**: Database URLs, messaging credentials
- **Client details**: Package name, certificate info

Example structure:
```json
{
  "project_info": {
    "project_number": "123456789",
    "project_id": "ecomply-project",
    "name": "E-Comply"
  },
  "client": [
    {
      "client_info": {
        "mobilesdk_app_id": "1:123456789:android:abc...",
        "android_client_info": {
          "package_name": "com.example.e_comply",
          "certificate_hash": ["YOUR_SHA1_HASH"]
        }
      },
      "api_key": [
        {
          "current_key": "YOUR_API_KEY"
        }
      ],
      "services": {
        "appinvite_service": {
          "other_platform_oauth_client": []
        },
        "ads_service": {
          "status": 2
        }
      }
    }
  ],
  "configuration_version": "1"
}
```

## Troubleshooting

### Issue: Build still fails after adding google-services.json
**Solution:**
1. Close Android Studio
2. Delete the `build/` folder from the `app/` directory
3. Delete the `.gradle/` folder from the project root
4. Reopen Android Studio and rebuild

### Issue: SHA1 mismatch error
**Solution:**
1. Get your debug SHA1 from Android Studio (Tools → Gradle → signingReport)
2. Go to Firebase Console → Project Settings → Your App
3. Update the SHA1 certificate

### Issue: Wrong package name
**Solution:**
1. Verify your package name in `AndroidManifest.xml` matches the one in Firebase
2. Or download a new `google-services.json` with the correct package name

## Backend Firebase Configuration

For the Python backend, you also need a Firebase service account key:

### Step 1: Create Service Account
1. Go to Firebase Console → Project Settings (gear icon)
2. Click **"Service Accounts"** tab
3. Click **"Generate New Private Key"**
4. Save the JSON file as `backend/firebase-credentials.json`

### Step 2: Update .env
Create `backend/.env`:
```
DEBUG=False
HOST=0.0.0.0
PORT=5000
FLASK_ENV=production

# Firebase Configuration
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json

# OCR Configuration
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
USE_EASYOCR=False

# E-commerce Scraping
ENABLE_AMAZON_SCRAPING=True
ENABLE_FLIPKART_SCRAPING=True
SCRAPE_TIMEOUT=30

# IoT Configuration
IOT_DEVICE_SECRET=your-secure-secret-key-here
MAX_IMAGE_SIZE_MB=5
```

## Security Notes

⚠️ **IMPORTANT:**
1. **Never commit** `google-services.json` or `firebase-credentials.json` to git
2. Add to `.gitignore`:
   ```
   app/google-services.json
   backend/firebase-credentials.json
   ```
3. These files contain sensitive credentials
4. Use Firebase Key Restrictions:
   - Restrict API keys in Firebase Console
   - Set appropriate usage limits
   - IP restrict server credentials

## Testing Firebase Connection

After adding the file, test the connection:

### In Android:
1. Run the app on a physical device or emulator
2. Open **Logcat** (View → Tool Windows → Logcat)
3. Search for "FirebaseApp"
4. You should see a message confirming Firebase initialization

### In Backend:
```bash
cd backend
python -c "import firebase_admin; from firebase_admin import credentials; creds = credentials.Certificate('firebase-credentials.json'); print('Firebase credentials loaded successfully')"
```

## Additional Resources

- [Firebase Console](https://console.firebase.google.com/)
- [Android Firebase Setup](https://firebase.google.com/docs/android/setup)
- [Firebase Service Accounts](https://firebase.google.com/docs/database/service-account)
- [Google Play Services Plugin](https://developers.google.com/android/guides/google-services-plugin)

## Next Steps

1. ✅ Download and place `google-services.json` in the `app/` folder
2. ✅ Download and place `firebase-credentials.json` in the `backend/` folder
3. ✅ Clean and rebuild the project
4. ✅ Run the app to verify Firebase is working
