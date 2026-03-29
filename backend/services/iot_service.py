import logging
from datetime import datetime
from services.ocr_service import OCRService
from services.compliance_service import ComplianceService

logger = logging.getLogger(__name__)

class IoTService:
    """Service for processing IoT device data"""
    
    def __init__(self):
        """Initialize IoT service"""
        self.ocr_service = OCRService()
        self.compliance_service = ComplianceService()
        self.registered_devices = set()  # In production, use database
    
    def process_device_data(self, device_id, image_base64=None, sensor_data=None):
        """
        Process data from IoT device
        
        Args:
            device_id: Unique device identifier
            image_base64: Base64 encoded image (optional)
            sensor_data: Sensor readings dictionary (optional)
            
        Returns:
            dict: Processing result with compliance report
        """
        try:
            logger.info(f"Processing data from IoT device: {device_id}")
            
            result = {
                'deviceId': device_id,
                'success': True,
                'message': 'Data processed successfully',
                'timestamp': int(datetime.now().timestamp() * 1000),
                'report': None
            }
            
            # Validate device (in production, check device registration)
            if not self.validate_device(device_id):
                result['success'] = False
                result['message'] = 'Device not registered'
                return result
            
            # Process image if provided
            if image_base64:
                try:
                    # Extract text from image
                    ocr_result = self.ocr_service.extract_text_from_base64(
                        image_base64,
                        source='iot'
                    )
                    
                    # Create product object from extracted data
                    product = self.create_product_from_ocr(
                        ocr_result,
                        device_id,
                        sensor_data
                    )
                    
                    # Validate compliance
                    compliance_report = self.compliance_service.validate_product(
                        product,
                        ocr_result['text']
                    )
                    
                    result['report'] = compliance_report
                    result['message'] = 'Image processed and compliance validated'
                    
                except Exception as e:
                    logger.error(f"Image processing failed: {str(e)}")
                    result['success'] = False
                    result['message'] = f'Image processing failed: {str(e)}'
            
            # Process sensor data if provided
            if sensor_data:
                result['sensorData'] = self.process_sensor_data(sensor_data)
            
            # Log device activity
            self.log_device_activity(device_id, result)
            
            return result
            
        except Exception as e:
            logger.error(f"IoT data processing failed: {str(e)}")
            return {
                'deviceId': device_id,
                'success': False,
                'message': f'Processing failed: {str(e)}',
                'timestamp': int(datetime.now().timestamp() * 1000)
            }
    
    def validate_device(self, device_id):
        """
        Validate if device is registered
        
        Args:
            device_id: Device identifier
            
        Returns:
            bool: True if device is valid
        """
        # In production, verify against database
        # For now, accept all devices that match pattern
        if not device_id or len(device_id) < 8:
            return False
        
        # Auto-register device for demo purposes
        self.registered_devices.add(device_id)
        return True
    
    def create_product_from_ocr(self, ocr_result, device_id, sensor_data):
        """
        Create product object from OCR results
        
        Args:
            ocr_result: OCR extraction result
            device_id: Device identifier
            sensor_data: Additional sensor data
            
        Returns:
            dict: Product object
        """
        structured_data = ocr_result.get('structured_data', {})
        
        product = {
            'id': self.generate_product_id(),
            'name': 'IoT Scanned Product',
            'manufacturerName': '',
            'manufacturerAddress': '',
            'netQuantity': structured_data.get('netQuantity', ''),
            'mrp': structured_data.get('mrp', ''),
            'manufacturingDate': structured_data.get('manufacturingDate', ''),
            'expiryDate': '',
            'customerCareDetails': structured_data.get('customerCare', ''),
            'countryOfOrigin': structured_data.get('countryOfOrigin', ''),
            'scannedText': ocr_result.get('text', ''),
            'source': 'IOT_DEVICE',
            'scannedBy': f'iot_{device_id}'
        }
        
        # Enhance with sensor data if available
        if sensor_data:
            if 'temperature' in sensor_data:
                product['sensorTemperature'] = sensor_data['temperature']
            if 'humidity' in sensor_data:
                product['sensorHumidity'] = sensor_data['humidity']
        
        return product
    
    def process_sensor_data(self, sensor_data):
        """
        Process and validate sensor readings
        
        Args:
            sensor_data: Dictionary of sensor readings
            
        Returns:
            dict: Processed sensor data with validations
        """
        processed = {
            'readings': sensor_data,
            'alerts': []
        }
        
        # Check temperature thresholds
        if 'temperature' in sensor_data:
            temp = sensor_data['temperature']
            if temp > 50:
                processed['alerts'].append({
                    'type': 'HIGH_TEMPERATURE',
                    'message': f'Temperature {temp}°C exceeds safe limit',
                    'severity': 'WARNING'
                })
            elif temp < 0:
                processed['alerts'].append({
                    'type': 'LOW_TEMPERATURE',
                    'message': f'Temperature {temp}°C below safe limit',
                    'severity': 'WARNING'
                })
        
        # Check humidity thresholds
        if 'humidity' in sensor_data:
            humidity = sensor_data['humidity']
            if humidity > 80:
                processed['alerts'].append({
                    'type': 'HIGH_HUMIDITY',
                    'message': f'Humidity {humidity}% exceeds safe limit',
                    'severity': 'WARNING'
                })
            elif humidity < 20:
                processed['alerts'].append({
                    'type': 'LOW_HUMIDITY',
                    'message': f'Humidity {humidity}% below safe limit',
                    'severity': 'INFO'
                })
        
        return processed
    
    def log_device_activity(self, device_id, result):
        """
        Log device activity for monitoring
        
        Args:
            device_id: Device identifier
            result: Processing result
        """
        # In production, log to database or monitoring system
        logger.info(f"Device {device_id} activity logged: {result['success']}")
    
    def generate_product_id(self):
        """Generate unique product ID"""
        import uuid
        return str(uuid.uuid4())
    
    def get_device_history(self, device_id):
        """
        Get activity history for a device
        
        Args:
            device_id: Device identifier
            
        Returns:
            list: Device activity history
        """
        # In production, fetch from database
        return []
    
    def register_device(self, device_id, device_info):
        """
        Register a new IoT device
        
        Args:
            device_id: Device identifier
            device_info: Device information dictionary
            
        Returns:
            dict: Registration result
        """
        try:
            self.registered_devices.add(device_id)
            
            logger.info(f"Device registered: {device_id}")
            
            return {
                'success': True,
                'message': 'Device registered successfully',
                'deviceId': device_id
            }
        except Exception as e:
            logger.error(f"Device registration failed: {str(e)}")
            return {
                'success': False,
                'message': f'Registration failed: {str(e)}'
            }
