from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from config import Config
from functools import wraps
import logging
import io
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
from services.compliance_analyzer import ComplianceAnalyzer
from services.pdf_service import PDFService
from services.crawler_service import CrawlerService
from services.category_service import CategoryService
from services.gemini_service import GeminiService
from services.risk_prediction_service import RiskPredictionService

# Initialize services
ocr_service = OCRService()
compliance_service = ComplianceService()
ecommerce_service = EcommerceService()
iot_service = IoTService()
compliance_analyzer = ComplianceAnalyzer(
    gemini_api_key=Config.GEMINI_API_KEY if Config.USE_GEMINI else "",
    use_ml_risk=Config.USE_ML_RISK,
)
pdf_service = PDFService()
crawler_service = CrawlerService(analyzer=compliance_analyzer)
category_service = CategoryService()
gemini_service = GeminiService(api_key=Config.GEMINI_API_KEY if Config.USE_GEMINI else "")
risk_service = RiskPredictionService()

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'E-Comply Backend is running'}), 200

# ═════════════════════════════════════════════════════════════════════════════
# OCR Routes
# ═════════════════════════════════════════════════════════════════════════════

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

# ═════════════════════════════════════════════════════════════════════════════
# Compliance Analysis Routes (NEW — structured JSON output)
# ═════════════════════════════════════════════════════════════════════════════

@app.route('/api/compliance/analyze', methods=['POST'])
@require_auth
def analyze_compliance():
    """
    Full compliance analysis pipeline.

    Accepts raw OCR text and returns the structured JSON compliance report
    with all 16 mandatory field validations, compliance score, risk level,
    and AI remarks.

    Request JSON:
        { "ocrText": "raw OCR text..." }
        OR
        { "imageBase64": "base64...", "source": "mobile" }

    Response: Structured compliance report JSON
    """
    try:
        data = request.get_json()

        # Option A: caller already has OCR text
        ocr_text = data.get('ocrText', '')

        # Option B: caller sends image — run OCR first
        if not ocr_text and data.get('imageBase64'):
            ocr_result = ocr_service.extract_text_from_base64(
                data['imageBase64'], data.get('source', 'mobile')
            )
            ocr_text = ocr_result.get('text', '')

        if not ocr_text:
            return jsonify({'error': 'ocrText or imageBase64 is required'}), 400

        report = compliance_analyzer.analyze(ocr_text)
        return jsonify(report), 200

    except Exception as e:
        logger.error(f"Compliance analysis error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ═════════════════════════════════════════════════════════════════════════════
# Legacy Compliance Validation (backward-compatible)
# ═════════════════════════════════════════════════════════════════════════════

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

# ═════════════════════════════════════════════════════════════════════════════
# Report Routes
# ═════════════════════════════════════════════════════════════════════════════

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

# ═════════════════════════════════════════════════════════════════════════════
# PDF Report Generation (NEW)
# ═════════════════════════════════════════════════════════════════════════════

@app.route('/api/reports/<report_id>/pdf', methods=['GET'])
@require_auth
def download_report_pdf(report_id):
    """
    Generate and download a professional PDF compliance report.

    Returns PDF file with proper headers for download.
    """
    try:
        # Fetch the report from Firestore
        report = compliance_service.get_report(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404

        # Generate PDF
        pdf_bytes = pdf_service.generate_pdf(report)

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'compliance_report_{report_id}.pdf',
        )

    except Exception as e:
        logger.error(f"PDF generation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/pdf/generate', methods=['POST'])
@require_auth
def generate_pdf_from_report():
    """
    Generate PDF from a report JSON payload (no Firestore lookup).

    Request JSON: full structured compliance report
    Response: PDF file download
    """
    try:
        report = request.get_json()
        if not report or 'report_id' not in report:
            return jsonify({'error': 'Valid report JSON is required'}), 400

        pdf_bytes = pdf_service.generate_pdf(report)

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'compliance_report_{report["report_id"]}.pdf',
        )

    except Exception as e:
        logger.error(f"PDF generation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ═════════════════════════════════════════════════════════════════════════════
# Category Detection (NEW)
# ═════════════════════════════════════════════════════════════════════════════

@app.route('/api/category/detect', methods=['POST'])
@require_auth
def detect_category():
    """Detect product category from text."""
    try:
        data = request.get_json()
        text = data.get('text', '')
        if not text:
            return jsonify({'error': 'text is required'}), 400

        category = category_service.detect_category(text)
        return jsonify({'category': category}), 200

    except Exception as e:
        logger.error(f"Category detection error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ═════════════════════════════════════════════════════════════════════════════
# Web Crawler Routes (NEW)
# ═════════════════════════════════════════════════════════════════════════════

@app.route('/api/crawler/scan', methods=['POST'])
@require_auth
def crawler_scan():
    """
    Trigger a single crawl of a product URL and return compliance report.

    Request JSON:
        { "url": "https://..." }
    """
    try:
        data = request.get_json()
        url = data.get('url')
        if not url:
            return jsonify({'error': 'url is required'}), 400

        # Crawl product data
        product_data = crawler_service.extract_product_data(url)
        if 'error' in product_data:
            return jsonify({'error': product_data['error']}), 400

        # Build pseudo-OCR text from crawled fields
        ocr_lines = []
        for key, value in product_data.items():
            if key not in ('source_url', 'crawled_at', 'error'):
                ocr_lines.append(f"{key}: {value}")
        ocr_text = '\n'.join(ocr_lines)

        # Run compliance analysis
        report = compliance_analyzer.analyze(ocr_text)
        report['data_source'] = 'WEB_CRAWLER'
        report['source_url'] = url

        return jsonify(report), 200

    except Exception as e:
        logger.error(f"Crawler scan error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/crawler/start', methods=['POST'])
@require_auth
def start_crawler():
    """Start automated scheduled scanning."""
    try:
        data = request.get_json() or {}
        interval = data.get('interval', 3600)  # Default 1 hour
        crawler_service.start_scheduled_scanning(interval=interval)
        return jsonify({
            'status': 'started',
            'interval': interval,
            'message': 'Automated e-commerce monitoring started'
        }), 200
    except Exception as e:
        logger.error(f"Failed to start crawler: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/crawler/stop', methods=['POST'])
@require_auth
def stop_crawler():
    """Stop automated scheduled scanning."""
    try:
        crawler_service.stop_scheduled_scanning()
        return jsonify({
            'status': 'stopped',
            'message': 'Automated e-commerce monitoring stopped'
        }), 200
    except Exception as e:
        logger.error(f"Failed to stop crawler: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/crawler/status', methods=['GET'])
@require_auth
def crawler_status():
    """Get crawler status and statistics."""
    return jsonify({
        'running': crawler_service._running,
        'stats': crawler_service.stats,
        'seed_urls': crawler_service.SEED_URLS
    }), 200

# ═════════════════════════════════════════════════════════════════════════════
# Inspector Analytics (NEW)
# ═════════════════════════════════════════════════════════════════════════════

@app.route('/api/inspector/analytics', methods=['GET'])
@require_auth
def get_inspector_analytics():
    """
    Get aggregated analytics for the inspector dashboard.

    Returns category-wise violations, risk distribution,
    compliance trends, etc.
    """
    try:
        reports = compliance_service.get_inspector_reports()

        # Calculate analytics
        total = len(reports)
        if total == 0:
            return jsonify({
                'total_reports': 0,
                'average_score': 0,
                'risk_distribution': {},
                'category_violations': {},
                'compliance_trend': [],
            }), 200

        scores = [r.get('complianceScore', 0) for r in reports]
        avg_score = sum(scores) / len(scores)

        # Risk distribution
        risk_dist = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0}
        for r in reports:
            level = r.get('riskLevel', 'LOW')
            risk_dist[level] = risk_dist.get(level, 0) + 1

        # Status distribution
        status_dist = {}
        for r in reports:
            s = r.get('complianceStatus', 'UNKNOWN')
            status_dist[s] = status_dist.get(s, 0) + 1

        return jsonify({
            'total_reports': total,
            'average_score': round(avg_score, 2),
            'risk_distribution': risk_dist,
            'status_distribution': status_dist,
        }), 200

    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ═════════════════════════════════════════════════════════════════════════════
# AI-Powered Validation (Gemini NLP + ML Risk)
# ═════════════════════════════════════════════════════════════════════════════

@app.route('/api/ai/validate', methods=['POST'])
@require_auth
def ai_validate():
    """
    Full AI-powered compliance validation using Gemini NLP.

    Runs: Gemini field extraction → semantic validation → AI remarks.
    Falls back to regex-based extraction if Gemini unavailable.

    Request JSON:
        { "ocrText": "raw OCR text..." }
    """
    try:
        data = request.get_json()
        ocr_text = data.get('ocrText', '')

        if not ocr_text and data.get('imageBase64'):
            ocr_result = ocr_service.extract_text_from_base64(
                data['imageBase64'], data.get('source', 'mobile')
            )
            ocr_text = ocr_result.get('text', '')

        if not ocr_text:
            return jsonify({'error': 'ocrText or imageBase64 is required'}), 400

        # Run full AI analysis
        if gemini_service.is_available:
            result = gemini_service.full_analysis(ocr_text)
        else:
            result = {
                "gemini_available": False,
                "message": "Gemini API not configured. Set GEMINI_API_KEY in .env"
            }

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"AI validation error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/risk', methods=['POST'])
@require_auth
def ai_risk_prediction():
    """
    ML-powered risk level prediction.

    Request JSON:
        { "fields": { "mrp": "50", "manufacturer_name": "Tata", ... },
          "category": "Food" }
    """
    try:
        data = request.get_json()
        fields = data.get('fields', {})
        category = data.get('category', '')

        if not fields:
            return jsonify({'error': 'fields dict is required'}), 400

        prediction = risk_service.predict(fields, category)
        return jsonify(prediction), 200

    except Exception as e:
        logger.error(f"Risk prediction error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ═════════════════════════════════════════════════════════════════════════════
# E-commerce Routes
# ═════════════════════════════════════════════════════════════════════════════

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

# ═════════════════════════════════════════════════════════════════════════════
# IoT Routes
# ═════════════════════════════════════════════════════════════════════════════

@app.route('/api/iot/data', methods=['POST'])
def process_iot_data():
    """Process data from IoT device (ESP32)"""
    try:
        data = request.get_json()
        device_id = data.get('deviceId')
        image_base64 = data.get('imageBase64')
        sensor_data = data.get('sensorData', {})
        api_key = request.headers.get('X-API-Key', '')

        if not device_id:
            return jsonify({'error': 'Device ID is required'}), 400

        result = iot_service.process_device_data(
            device_id, image_base64, sensor_data, api_key=api_key
        )

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"IoT data processing error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/iot/register', methods=['POST'])
def register_iot_device():
    """Register a new IoT device (admin use)"""
    try:
        data = request.get_json()
        device_id = data.get('deviceId')
        device_info = data.get('deviceInfo', {})

        if not device_id:
            return jsonify({'error': 'Device ID is required'}), 400

        result = iot_service.register_device(device_id, device_info)
        status_code = 200 if result.get('success') else 500
        return jsonify(result), status_code

    except Exception as e:
        logger.error(f"IoT device registration error: {str(e)}")
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
