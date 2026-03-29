/*
 * E-Comply IoT Device - ESP32 Camera Module
 * 
 * This Arduino sketch enables ESP32 with camera module to capture 
 * product images and send them to the E-Comply backend for 
 * compliance validation.
 * 
 * Hardware Required:
 * - ESP32-CAM or ESP32 with OV2640 camera module
 * - Optional: DHT22 sensor for temperature/humidity monitoring
 * 
 * Libraries Required:
 * - ESP32 Camera library
 * - WiFi library
 * - HTTPClient library
 * - ArduinoJson library (optional for sensor data)
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include "esp_camera.h"
#include "esp_http_client.h"
#include "base64.h"

// ===== CONFIGURATION =====
// WiFi Credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Backend Server Configuration
const char* serverUrl = "http://YOUR_SERVER_IP:5000/api/iot/data";
const char* deviceId = "ESP32_001";  // Unique device identifier

// Camera Pin Configuration (for ESP32-CAM)
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// Timing Configuration
const int scanInterval = 30000;  // Scan every 30 seconds
const int retryDelay = 5000;     // Retry delay on failure

// ===== GLOBAL VARIABLES =====
unsigned long lastScanTime = 0;

// ===== FUNCTION DECLARATIONS =====
void initCamera();
void initWiFi();
bool captureAndSendImage();
String encodeBase64(uint8_t* data, size_t length);
void sendToBackend(String base64Image);

// ===== SETUP =====
void setup() {
  Serial.begin(115200);
  Serial.println("\n\n=== E-Comply IoT Device Starting ===");
  
  // Initialize WiFi
  initWiFi();
  
  // Initialize Camera
  initCamera();
  
  Serial.println("=== E-Comply IoT Device Ready ===\n");
}

// ===== MAIN LOOP =====
void loop() {
  // Check if it's time to scan
  unsigned long currentTime = millis();
  
  if (currentTime - lastScanTime >= scanInterval) {
    Serial.println("\n--- Starting Product Scan ---");
    
    if (captureAndSendImage()) {
      Serial.println("--- Scan Completed Successfully ---\n");
    } else {
      Serial.println("--- Scan Failed ---\n");
    }
    
    lastScanTime = currentTime;
  }
  
  delay(1000);  // Small delay to prevent CPU overload
}

// ===== WIFI INITIALIZATION =====
void initWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWiFi Connection Failed!");
  }
}

// ===== CAMERA INITIALIZATION =====
void initCamera() {
  Serial.println("Initializing Camera...");
  
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  
  // Image quality settings
  if(psramFound()){
    config.frame_size = FRAMESIZE_UXGA;  // High resolution
    config.jpeg_quality = 10;             // Lower number = higher quality
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }
  
  // Initialize camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x\n", err);
    return;
  }
  
  Serial.println("Camera Initialized Successfully!");
  
  // Adjust camera settings for better text recognition
  sensor_t * s = esp_camera_sensor_get();
  if (s != NULL) {
    s->set_brightness(s, 0);     // -2 to 2
    s->set_contrast(s, 0);       // -2 to 2
    s->set_saturation(s, 0);     // -2 to 2
    s->set_special_effect(s, 0); // 0 = No effect
    s->set_whitebal(s, 1);       // 0 = disable, 1 = enable
    s->set_awb_gain(s, 1);       // 0 = disable, 1 = enable
    s->set_wb_mode(s, 0);        // 0 to 4
    s->set_exposure_ctrl(s, 1);  // 0 = disable, 1 = enable
    s->set_aec2(s, 0);           // 0 = disable, 1 = enable
    s->set_gain_ctrl(s, 1);      // 0 = disable, 1 = enable
    s->set_agc_gain(s, 0);       // 0 to 30
    s->set_gainceiling(s, (gainceiling_t)0);  // 0 to 6
    s->set_bpc(s, 0);            // 0 = disable, 1 = enable
    s->set_wpc(s, 1);            // 0 = disable, 1 = enable
    s->set_raw_gma(s, 1);        // 0 = disable, 1 = enable
    s->set_lenc(s, 1);           // 0 = disable, 1 = enable
    s->set_hmirror(s, 0);        // 0 = disable, 1 = enable
    s->set_vflip(s, 0);          // 0 = disable, 1 = enable
  }
}

// ===== CAPTURE AND SEND IMAGE =====
bool captureAndSendImage() {
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected. Attempting reconnection...");
    initWiFi();
    
    if (WiFi.status() != WL_CONNECTED) {
      return false;
    }
  }
  
  // Capture image
  Serial.println("Capturing image...");
  camera_fb_t * fb = esp_camera_fb_get();
  
  if (!fb) {
    Serial.println("Camera capture failed!");
    return false;
  }
  
  Serial.printf("Image captured: %d bytes\n", fb->len);
  
  // Encode to base64
  Serial.println("Encoding to base64...");
  String base64Image = encodeBase64(fb->buf, fb->len);
  
  // Return frame buffer
  esp_camera_fb_return(fb);
  
  // Send to backend
  sendToBackend(base64Image);
  
  return true;
}

// ===== BASE64 ENCODING =====
String encodeBase64(uint8_t* data, size_t length) {
  // Simple base64 encoding implementation
  const char* base64_chars = 
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
  
  String encoded = "";
  int i = 0;
  int j = 0;
  unsigned char char_array_3[3];
  unsigned char char_array_4[4];
  
  while (length--) {
    char_array_3[i++] = *(data++);
    if (i == 3) {
      char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
      char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + ((char_array_3[1] & 0xf0) >> 4);
      char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + ((char_array_3[2] & 0xc0) >> 6);
      char_array_4[3] = char_array_3[2] & 0x3f;
      
      for(i = 0; i < 4; i++)
        encoded += base64_chars[char_array_4[i]];
      i = 0;
    }
  }
  
  if (i) {
    for(j = i; j < 3; j++)
      char_array_3[j] = '\0';
    
    char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
    char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + ((char_array_3[1] & 0xf0) >> 4);
    char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + ((char_array_3[2] & 0xc0) >> 6);
    char_array_4[3] = char_array_3[2] & 0x3f;
    
    for (j = 0; j < i + 1; j++)
      encoded += base64_chars[char_array_4[j]];
    
    while(i++ < 3)
      encoded += '=';
  }
  
  return encoded;
}

// ===== SEND TO BACKEND =====
void sendToBackend(String base64Image) {
  Serial.println("Sending to backend server...");
  
  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(30000);  // 30 second timeout
  
  // Create JSON payload
  String payload = "{";
  payload += "\"deviceId\":\"" + String(deviceId) + "\",";
  payload += "\"imageBase64\":\"" + base64Image + "\",";
  payload += "\"sensorData\":{";
  payload += "\"temperature\":25.5,";  // Replace with actual sensor reading
  payload += "\"humidity\":60";        // Replace with actual sensor reading
  payload += "}";
  payload += "}";
  
  Serial.printf("Payload size: %d bytes\n", payload.length());
  
  // Send POST request
  int httpResponseCode = http.POST(payload);
  
  // Handle response
  if (httpResponseCode > 0) {
    Serial.printf("HTTP Response code: %d\n", httpResponseCode);
    String response = http.getString();
    Serial.println("Response: " + response);
  } else {
    Serial.printf("HTTP Error: %s\n", http.errorToString(httpResponseCode).c_str());
  }
  
  http.end();
}
