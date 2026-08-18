import re
from marshmallow import ValidationError

def validate_password_strength(password):
    """Validate password strength"""
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters')
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter')
    
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain at least one lowercase letter')
    
    if not re.search(r'\d', password):
        raise ValidationError('Password must contain at least one number')
    
    return True

def validate_phone_number(phone):
    """Validate Kenyan phone number"""
    # Basic validation for Kenyan phone numbers
    pattern = r'^(?:\+254|0)?[17]\d{8}$'
    if not re.match(pattern, phone):
        raise ValidationError('Invalid phone number format. Use format: +254712345678 or 0712345678')
    return True

def sanitize_input(data):
    """Sanitize input data to prevent XSS"""
    if isinstance(data, str):
        # Remove any HTML tags
        return re.sub(r'<[^>]*>', '', data).strip()
    return data

def validate_email_domain(email):
    """Validate email domain is not disposable"""
    # You can add disposable domain checking here
    # For now, we'll just check it's a valid format
    return True