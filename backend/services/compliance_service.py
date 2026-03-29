import re
import logging
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class ComplianceService:
    """Service for Legal Metrology compliance validation"""
    
    def __init__(self):
        """Initialize compliance service"""
        self.mandatory_fields = Config.MANDATORY_FIELDS
        
    def validate_product(self, product, extracted_text=''):
        """
        Validate product compliance with Legal Metrology rules
        
        Args:
            product: Product data dictionary
            extracted_text: Raw OCR extracted text
            
        Returns:
            dict: Compliance report
        """
        try:
            # Initialize report
            report = {
                'id': self.generate_report_id(),
                'productId': product.get('id', ''),
                'productName': product.get('name', ''),
                'complianceScore': 0.0,
                'isCompliant': False,
                'complianceStatus': 'PENDING',
                'missingFields': [],
                'violations': [],
                'recommendations': [],
                'riskLevel': 'LOW',
                'aiSummary': '',
                'createdAt': int(datetime.now().timestamp() * 1000),
                'updatedAt': int(datetime.now().timestamp() * 1000)
            }
            
            # Validate mandatory fields
            missing_fields, violations = self.check_mandatory_fields(product)
            report['missingFields'] = missing_fields
            report['violations'].extend(violations)
            
            # Validate field formats
            format_violations = self.validate_field_formats(product)
            report['violations'].extend(format_violations)
            
            # Calculate compliance score
            report['complianceScore'] = self.calculate_compliance_score(
                len(self.mandatory_fields),
                len(missing_fields),
                len(violations)
            )
            
            # Determine compliance status
            report['complianceStatus'] = self.determine_status(report['complianceScore'])
            report['isCompliant'] = report['complianceScore'] == 100.0
            
            # Determine risk level
            report['riskLevel'] = self.determine_risk_level(report['complianceScore'], violations)
            
            # Generate recommendations
            report['recommendations'] = self.generate_recommendations(
                missing_fields,
                violations
            )
            
            # Generate AI summary
            report['aiSummary'] = self.generate_ai_summary(product, report)
            
            logger.info(f"Compliance validation completed for product: {product.get('name')}")
            
            return report
            
        except Exception as e:
            logger.error(f"Compliance validation failed: {str(e)}")
            raise Exception(f"Failed to validate compliance: {str(e)}")
    
    def check_mandatory_fields(self, product):
        """
        Check if all mandatory fields are present
        
        Args:
            product: Product data dictionary
            
        Returns:
            tuple: (missing_fields, violations)
        """
        missing_fields = []
        violations = []
        
        field_mapping = {
            'Manufacturer Name': 'manufacturerName',
            'Manufacturer Address': 'manufacturerAddress',
            'Net Quantity': 'netQuantity',
            'MRP': 'mrp',
            'Manufacturing/Packing Date': 'manufacturingDate',
            'Customer Care Details': 'customerCareDetails',
            'Country of Origin': 'countryOfOrigin'
        }
        
        for field_name, field_key in field_mapping.items():
            field_value = product.get(field_key, '').strip()
            
            if not field_value:
                missing_fields.append(field_name)
                violations.append({
                    'field': field_name,
                    'description': f'{field_name} is missing or empty',
                    'severity': 'HIGH',
                    'ruleViolated': 'Legal Metrology (Packaged Commodities) Rules, 2011 - Section 6'
                })
        
        return missing_fields, violations
    
    def validate_field_formats(self, product):
        """
        Validate format of specific fields
        
        Args:
            product: Product data dictionary
            
        Returns:
            list: Format violations
        """
        violations = []
        
        # Validate net quantity format
        net_quantity = product.get('netQuantity', '')
        if net_quantity and not re.search(r'\d+\s*(?:kg|g|l|ml|unit|pcs|piece)', net_quantity, re.IGNORECASE):
            violations.append({
                'field': 'Net Quantity',
                'description': 'Net quantity format is invalid. Should include value and unit (kg/g/l/ml)',
                'severity': 'MEDIUM',
                'ruleViolated': 'Legal Metrology (Packaged Commodities) Rules, 2011 - Schedule I'
            })
        
        # Validate MRP format
        mrp = product.get('mrp', '')
        if mrp and not re.search(r'(?:MRP|Rs\.?|₹)\s*\d+', mrp, re.IGNORECASE):
            violations.append({
                'field': 'MRP',
                'description': 'MRP format is invalid. Should be clearly marked as "MRP" with price',
                'severity': 'HIGH',
                'ruleViolated': 'Legal Metrology (Packaged Commodities) Rules, 2011 - Section 18'
            })
        
        # Validate customer care details
        customer_care = product.get('customerCareDetails', '')
        has_phone = re.search(r'(?:\+91|0)?[\s-]?\d{3}[\s-]?\d{3}[\s-]?\d{4}', customer_care)
        has_email = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', customer_care)
        
        if customer_care and not (has_phone or has_email):
            violations.append({
                'field': 'Customer Care Details',
                'description': 'Customer care details should include phone number or email',
                'severity': 'MEDIUM',
                'ruleViolated': 'Legal Metrology (Packaged Commodities) Rules, 2011 - Section 6(h)'
            })
        
        return violations
    
    def calculate_compliance_score(self, total_fields, missing_fields, total_violations):
        """
        Calculate compliance score based on missing fields and violations
        
        Args:
            total_fields: Total mandatory fields
            missing_fields: Number of missing fields
            total_violations: Total number of violations
            
        Returns:
            float: Compliance score (0-100)
        """
        if total_fields == 0:
            return 100.0
        
        # Base score from mandatory fields
        field_score = ((total_fields - missing_fields) / total_fields) * 100
        
        # Penalty for format violations (non-missing field violations)
        format_violations = max(0, total_violations - missing_fields)
        penalty = min(format_violations * 5, 20)  # Max 20% penalty
        
        final_score = max(0, field_score - penalty)
        
        return round(final_score, 2)
    
    def determine_status(self, compliance_score):
        """
        Determine compliance status based on score
        
        Args:
            compliance_score: Compliance score (0-100)
            
        Returns:
            str: Compliance status
        """
        if compliance_score == 100:
            return 'COMPLIANT'
        elif compliance_score >= 70:
            return 'PARTIAL_COMPLIANT'
        else:
            return 'NON_COMPLIANT'
    
    def determine_risk_level(self, compliance_score, violations):
        """
        Determine risk level based on compliance score and violations
        
        Args:
            compliance_score: Compliance score
            violations: List of violations
            
        Returns:
            str: Risk level (LOW, MEDIUM, HIGH, CRITICAL)
        """
        # Check for critical violations
        critical_violations = [v for v in violations if v.get('severity') == 'CRITICAL']
        high_violations = [v for v in violations if v.get('severity') == 'HIGH']
        
        if critical_violations or compliance_score < 50:
            return 'CRITICAL'
        elif high_violations or compliance_score < 70:
            return 'HIGH'
        elif compliance_score < 90:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def generate_recommendations(self, missing_fields, violations):
        """
        Generate recommendations for compliance improvement
        
        Args:
            missing_fields: List of missing fields
            violations: List of violations
            
        Returns:
            list: Recommendations
        """
        recommendations = []
        
        if missing_fields:
            recommendations.append(
                f"Add the following mandatory information to the product label: {', '.join(missing_fields)}"
            )
        
        if any(v.get('severity') in ['HIGH', 'CRITICAL'] for v in violations):
            recommendations.append(
                "Immediately address high-priority violations to ensure legal compliance"
            )
        
        recommendations.extend([
            "Ensure all information is printed in legible font (minimum 1.5mm height)",
            "Verify that MRP is inclusive of all taxes",
            "Include complete manufacturer address with pin code",
            "Display customer care contact prominently on the package",
            "Ensure country of origin is clearly mentioned for imported goods"
        ])
        
        return recommendations
    
    def generate_ai_summary(self, product, report):
        """
        Generate AI-powered summary of compliance report
        
        Args:
            product: Product data
            report: Compliance report
            
        Returns:
            str: AI summary
        """
        product_name = product.get('name', 'The product')
        score = report['complianceScore']
        status = report['complianceStatus'].replace('_', ' ').lower()
        missing_count = len(report['missingFields'])
        violation_count = len(report['violations'])
        risk_level = report['riskLevel'].lower()
        
        summary_parts = []
        
        # Status summary
        if score == 100:
            summary_parts.append(
                f"{product_name} is fully compliant with Legal Metrology (Packaged Commodities) Rules, 2011. "
                f"All mandatory labeling requirements are met."
            )
        elif score >= 70:
            summary_parts.append(
                f"{product_name} is partially compliant with a score of {int(score)}%. "
                f"The product meets most requirements but has {violation_count} compliance issue(s) that need attention."
            )
        else:
            summary_parts.append(
                f"{product_name} is non-compliant with a score of {int(score)}%. "
                f"The product has {violation_count} significant compliance issues that must be resolved."
            )
        
        # Missing fields
        if missing_count > 0:
            summary_parts.append(
                f"{missing_count} mandatory field(s) are missing from the product label."
            )
        
        # Risk assessment
        if risk_level in ['high', 'critical']:
            summary_parts.append(
                f"This product poses a {risk_level} compliance risk and requires immediate corrective action. "
                f"Selling this product without proper labeling may result in penalties under Legal Metrology Act."
            )
        elif risk_level == 'medium':
            summary_parts.append(
                f"This product has moderate compliance risks that should be addressed promptly."
            )
        else:
            summary_parts.append(
                f"This product has minimal compliance risks and demonstrates good adherence to regulations."
            )
        
        return ' '.join(summary_parts)
    
    def generate_report_id(self):
        """Generate unique report ID"""
        import uuid
        return str(uuid.uuid4())
    
    def get_report(self, report_id):
        """
        Get compliance report by ID
        (In production, this would fetch from Firebase)
        """
        # Placeholder - implement Firebase integration
        return None
    
    def get_user_reports(self, user_id):
        """
        Get all reports for a user
        (In production, this would fetch from Firebase)
        """
        # Placeholder - implement Firebase integration
        return []
    
    def get_inspector_reports(self, status=None, risk_level=None):
        """
        Get reports for inspectors with optional filters
        (In production, this would fetch from Firebase)
        """
        # Placeholder - implement Firebase integration
        return []
