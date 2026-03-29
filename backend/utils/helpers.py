"""
Utility functions for the backend
"""

import re
from datetime import datetime
from typing import Dict, Any, List

def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if valid email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """
    Validate Indian phone number format
    
    Args:
        phone: Phone number to validate
        
    Returns:
        bool: True if valid phone format
    """
    # Remove spaces and hyphens
    phone = phone.replace(' ', '').replace('-', '')
    
    # Check various Indian phone patterns
    patterns = [
        r'^[6-9]\d{9}$',  # 10 digit mobile
        r'^\+91[6-9]\d{9}$',  # With +91
        r'^0[6-9]\d{9}$'  # With leading 0
    ]
    
    return any(bool(re.match(pattern, phone)) for pattern in patterns)

def format_date(timestamp: int) -> str:
    """
    Format timestamp to readable date
    
    Args:
        timestamp: Unix timestamp in milliseconds
        
    Returns:
        str: Formatted date string
    """
    try:
        dt = datetime.fromtimestamp(timestamp / 1000)
        return dt.strftime('%d %b %Y, %I:%M %p')
    except:
        return 'Invalid date'

def extract_number_from_text(text: str) -> float:
    """
    Extract first number from text
    
    Args:
        text: Text containing numbers
        
    Returns:
        float: Extracted number or 0.0
    """
    match = re.search(r'\d+\.?\d*', text)
    return float(match.group(0)) if match else 0.0

def clean_text(text: str) -> str:
    """
    Clean and normalize text
    
    Args:
        text: Input text
        
    Returns:
        str: Cleaned text
    """
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove special characters except common punctuation
    text = re.sub(r'[^\w\s.,!?@-]', '', text)
    
    return text.strip()

def calculate_percentage(part: float, total: float) -> float:
    """
    Calculate percentage
    
    Args:
        part: Part value
        total: Total value
        
    Returns:
        float: Percentage
    """
    if total == 0:
        return 0.0
    return round((part / total) * 100, 2)

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks
    
    Args:
        lst: Input list
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage
    
    Args:
        filename: Input filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove or replace unsafe characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    filename = filename.replace(' ', '_')
    return filename[:255]  # Limit length

def generate_unique_id() -> str:
    """
    Generate unique identifier
    
    Returns:
        str: Unique ID
    """
    import uuid
    return str(uuid.uuid4())

def merge_dicts(*dicts: Dict) -> Dict:
    """
    Merge multiple dictionaries
    
    Args:
        *dicts: Variable number of dictionaries
        
    Returns:
        Dict: Merged dictionary
    """
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result

def get_file_extension(filename: str) -> str:
    """
    Get file extension
    
    Args:
        filename: Filename with extension
        
    Returns:
        str: File extension (without dot)
    """
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''

def is_valid_url(url: str) -> bool:
    """
    Validate URL format
    
    Args:
        url: URL to validate
        
    Returns:
        bool: True if valid URL
    """
    pattern = r'^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)$'
    return bool(re.match(pattern, url))

def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)].rstrip() + suffix

def parse_quantity(quantity_str: str) -> Dict[str, Any]:
    """
    Parse quantity string into value and unit
    
    Args:
        quantity_str: Quantity string (e.g., "500g", "1.5kg")
        
    Returns:
        Dict: {'value': float, 'unit': str}
    """
    match = re.match(r'(\d+\.?\d*)\s*([a-zA-Z]+)', quantity_str)
    if match:
        return {
            'value': float(match.group(1)),
            'unit': match.group(2).lower()
        }
    return {'value': 0.0, 'unit': ''}

def normalize_unit(unit: str) -> str:
    """
    Normalize unit to standard format
    
    Args:
        unit: Unit string
        
    Returns:
        str: Normalized unit
    """
    unit_map = {
        'kg': 'kg',
        'kilogram': 'kg',
        'g': 'g',
        'gram': 'g',
        'gm': 'g',
        'l': 'l',
        'liter': 'l',
        'litre': 'l',
        'ml': 'ml',
        'milliliter': 'ml',
        'millilitre': 'ml'
    }
    return unit_map.get(unit.lower(), unit.lower())
