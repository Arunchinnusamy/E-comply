from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from functools import wraps
import logging
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)
CORS(app)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ─── Firebase Admin SDK initialisation ───────────────────────────────────────
# Guard against double-initialisation (e.g. during hot-reload in debug mode)
if not firebase_admin._apps:
    cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)
    logger.info("Firebase Admin SDK initialised")

# ─── Auth decorator ───────────────────────────────────────────────────────────
def require_auth(f):
    """Verify the Firebase ID token supplied in the Authorization header.

    Attaches ``request.uid`` and ``request.user_email`` for use in route
    handlers.  Returns 401 for missing, expired, or invalid tokens.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authorization header missing or malformed"}), 401

        token = auth_header.split("Bearer ", 1)[1].strip()
        try:
            decoded = firebase_auth.verify_id_token(token)
            request.uid = decoded["uid"]
            request.user_email = decoded.get("email", "")
        except firebase_auth.ExpiredIdTokenError:
            return jsonify({"error": "Token has expired – please re-authenticate"}), 401
        except firebase_auth.RevokedIdTokenError:
            return jsonify({"error": "Token has been revoked – please re-authenticate"}), 401
        except firebase_auth.InvalidIdTokenError:
            return jsonify({"error": "Invalid token"}), 401
        except Exception as e:
            logger.error(f"Auth verification error: {str(e)}")
            return jsonify({"error": "Authentication failed"}), 401

        return f(*args, **kwargs)
    return decorated_function

# Import services
from services.ocr_service import OCRService
from services.compliance_service import ComplianceService
from services.ecommerce_service import EcommerceService
from services.iot_service import IoTService

# Initialize services
ocr_service = OCRService()
compliance_service = ComplianceService()
ecommerce_service = EcommerceService()
iot_service = IoTService()

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'E-Comply Backend is running'}), 200

# OCR Routes
@app.route('/api/ocr/extract', methods=['POST'])
@require_auth
def extract_text():
    """Extract text from product image using OCR"""
    try:
        data = request.get_json()
        image_base64 = data.get('imageBase64')
        source = data.get('source', 'mobile')
        
        if not image_base64:
            return jsonify({'error': 'Image data is required'}), 400
        
        result = ocr_service.extract_text_from_base64(image_base64, source)
        
        return jsonify({
            'extractedText': result['text'],
            'confidence': result['confidence'],
            'structuredData': result['structured_data']
        }), 200
        
    except Exception as e:
        logger.error(f"OCR extraction error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Compliance Routes
@app.route('/api/compliance/validate', methods=['POST'])
@require_auth
def validate_compliance():
    """Validate product compliance with Legal Metrology rules"""
    try:
        data = request.get_json()
        product = data.get('product')
        extracted_text = data.get('extractedText', '')
        
        if not product:
            return jsonify({'error': 'Product data is required'}), 400
        
        report = compliance_service.validate_product(product, extracted_text)
        
        return jsonify({
            'report': report,
            'success': True,
            'message': 'Compliance validation completed'
        }), 200
        
    except Exception as e:
        logger.error(f"Compliance validation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/<report_id>', methods=['GET'])
@require_auth
def get_report(report_id):
    """Get a specific compliance report"""
    try:
        report = compliance_service.get_report(report_id)
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        return jsonify(report), 200
        
    except Exception as e:
        logger.error(f"Get report error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/user/<user_id>', methods=['GET'])
@require_auth
def get_user_reports(user_id):
    """Get all reports for a specific user"""
    try:
        reports = compliance_service.get_user_reports(user_id)
        return jsonify(reports), 200
        
    except Exception as e:
        logger.error(f"Get user reports error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/inspector', methods=['GET'])
@require_auth
def get_inspector_reports():
    """Get all reports for inspectors with optional filters"""
    try:
        status = request.args.get('status')
        risk_level = request.args.get('riskLevel')
        
        reports = compliance_service.get_inspector_reports(status, risk_level)
        return jsonify(reports), 200
        
    except Exception as e:
        logger.error(f"Get inspector reports error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# E-commerce Routes
@app.route('/api/ecommerce/scrape', methods=['POST'])
@require_auth
def scrape_ecommerce():
    """Scrape product information from e-commerce platform"""
    try:
        data = request.get_json()
        url = data.get('url')
        platform = data.get('platform', 'auto')
        
        if not url:
            return jsonify({'error': 'Product URL is required'}), 400
        
        product = ecommerce_service.scrape_product(url, platform)
        
        return jsonify({
            'product': product,
            'success': True,
            'message': 'Product scraped successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"E-commerce scraping error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# IoT Routes
@app.route('/api/iot/data', methods=['POST'])
def process_iot_data():
    """Process data from IoT device (ESP32)"""
    try:
        data = request.get_json()
        device_id = data.get('deviceId')
        image_base64 = data.get('imageBase64')
        sensor_data = data.get('sensorData', {})
        
        if not device_id:
            return jsonify({'error': 'Device ID is required'}), 400
        
        result = iot_service.process_device_data(device_id, image_base64, sensor_data)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"IoT data processing error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info(f"Starting E-Comply Backend on {app.config['HOST']}:{app.config['PORT']}")
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
