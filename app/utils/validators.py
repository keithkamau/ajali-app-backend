import re

def is_valid_email(email):
    """Validate email format"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_password(password):
    """Validate password strength"""
    if not password or len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    if not any(c in '!@#$%^&*()_+-=[]{};:\'",.<>/?\\|`~' for c in password):
        return False
    return True

def is_valid_phone(phone):
    """Validate Kenyan phone number format"""
    if not phone:
        return True  # Phone number is optional
    pattern = r'^(?:\+254|0)(7|1)\d{8}$'
    return re.match(pattern, phone) is not None

def sanitize_input(text):
    """Sanitize user input"""
    if not text:
        return text
    # Remove leading/trailing whitespace
    return text.strip()

def validate_uuid(uuid_string):
    """Validate UUID format"""
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return re.match(pattern, str(uuid_string)) is not None