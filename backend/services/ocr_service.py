import base64
import cv2
import numpy as np
from PIL import Image
import pytesseract
import io
import re
import logging

logger = logging.getLogger(__name__)

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    logger.warning("EasyOCR not available, using Tesseract only")

class OCRService:
    """Service for optical character recognition"""
    
    def __init__(self):
        """Initialize OCR service"""
        if EASYOCR_AVAILABLE:
            try:
                self.reader = easyocr.Reader(['en'], gpu=False)
                logger.info("EasyOCR initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize EasyOCR: {str(e)}")
                self.reader = None
        else:
            self.reader = None
    
    def extract_text_from_base64(self, image_base64, source='mobile'):
        """
        Extract text from base64 encoded image
        
        Args:
            image_base64: Base64 encoded image string
            source: Source of the image (mobile, iot, etc.)
            
        Returns:
            dict: Extracted text, confidence, and structured data
        """
        try:
            # Decode base64 image
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Preprocess image
            processed_image = self.preprocess_image(opencv_image)
            
            # Extract text using available OCR engine
            if self.reader and EASYOCR_AVAILABLE:
                text, confidence = self.extract_with_easyocr(processed_image)
            else:
                text, confidence = self.extract_with_tesseract(processed_image)
            
            # Extract structured data
            structured_data = self.extract_structured_data(text)
            
            return {
                'text': text,
                'confidence': confidence,
                'structured_data': structured_data
            }
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            raise Exception(f"Failed to extract text: {str(e)}")
    
    def preprocess_image(self, image):
        """
        Preprocess image for better OCR results
        
        Args:
            image: OpenCV image
            
        Returns:
            Preprocessed image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Dilation and erosion to remove noise
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.dilate(thresh, kernel, iterations=1)
        processed = cv2.erode(processed, kernel, iterations=1)
        
        return processed
    
    def extract_with_easyocr(self, image):
        """
        Extract text using EasyOCR
        
        Args:
            image: Preprocessed image
            
        Returns:
            tuple: (text, confidence)
        """
        try:
            results = self.reader.readtext(image)
            
            if not results:
                return "", 0.0
            
            # Combine all detected text
            texts = [result[1] for result in results]
            confidences = [result[2] for result in results]
            
            combined_text = '\n'.join(texts)
            average_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return combined_text, average_confidence
            
        except Exception as e:
            logger.error(f"EasyOCR extraction failed: {str(e)}")
            return "", 0.0
    
    def extract_with_tesseract(self, image):
        """
        Extract text using Tesseract OCR
        
        Args:
            image: Preprocessed image
            
        Returns:
            tuple: (text, confidence)
        """
        try:
            # Extract text
            text = pytesseract.image_to_string(image)
            
            # Get confidence data
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if conf != '-1']
            
            average_confidence = sum(confidences) / len(confidences) / 100 if confidences else 0.0
            
            return text, average_confidence
            
        except Exception as e:
            logger.error(f"Tesseract extraction failed: {str(e)}")
            return "", 0.0
    
    def extract_structured_data(self, text):
        """
        Extract structured information from text
        
        Args:
            text: Extracted text
            
        Returns:
            dict: Structured data with identified fields
        """
        structured_data = {}
        
        # Extract MRP
        mrp_patterns = [
            r'MRP[:\s]*Rs\.?\s*(\d+)',
            r'M\.R\.P\.?[:\s]*Rs\.?\s*(\d+)',
            r'₹\s*(\d+)',
            r'Rs\.?\s*(\d+)'
        ]
        for pattern in mrp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                structured_data['mrp'] = match.group(1)
                break
        
        # Extract net quantity
        quantity_patterns = [
            r'(\d+\s*(?:kg|g|l|ml|unit|pcs|piece))',
            r'Net\s*(?:Qty|Quantity|Wt|Weight)[:\s]*(\d+\s*(?:kg|g|l|ml))'
        ]
        for pattern in quantity_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                structured_data['netQuantity'] = match.group(1)
                break
        
        # Extract dates
        date_patterns = [
            r'(?:Mfg|Manufacturing|Packed|Packing)\s*(?:Date)?[:\s]*(\d{2}[-/]\d{2}[-/]\d{2,4})',
            r'(\d{2}[-/]\d{2}[-/]\d{2,4})'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                structured_data['manufacturingDate'] = match.group(1)
                break
        
        # Extract country of origin
        country_patterns = [
            r'(?:Country of Origin|Made in)[:\s]*([A-Za-z\s]+)',
            r'(?:India|China|USA|Germany|Japan)'
        ]
        for pattern in country_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                structured_data['countryOfOrigin'] = match.group(1).strip() if match.lastindex else match.group(0)
                break
        
        # Extract phone numbers (customer care)
        phone_pattern = r'(?:\+91|0)?[\s-]?\d{3}[\s-]?\d{3}[\s-]?\d{4}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            structured_data['customerCare'] = phone_match.group(0)
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            if 'customerCare' in structured_data:
                structured_data['customerCare'] += f", {email_match.group(0)}"
            else:
                structured_data['customerCare'] = email_match.group(0)
        
        return structured_data
