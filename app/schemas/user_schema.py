from marshmallow import Schema, fields, validate, ValidationError
import re

def validate_phone(value):
    """Validate Kenyan phone number format"""
    if value is None:
        return
    pattern = r'^(?:\+254|0)(7|1)\d{8}$'
    if not re.match(pattern, value):
        raise ValidationError('Invalid phone number format. Use +2547XXXXXXXX or 07XXXXXXXX')

def validate_password(value):
    """Validate password strength"""
    if len(value) < 8:
        raise ValidationError('Password must be at least 8 characters long')
    if not any(c.isupper() for c in value):
        raise ValidationError('Password must contain at least one uppercase letter')
    if not any(c.islower() for c in value):
        raise ValidationError('Password must contain at least one lowercase letter')
    if not any(c.isdigit() for c in value):
        raise ValidationError('Password must contain at least one number')
    if not any(c in '!@#$%^&*()_+-=[]{};:\'",.<>/?\\|`~' for c in value):
        raise ValidationError('Password must contain at least one special character')
    return value

class RegisterSchema(Schema):
    """Registration request validation"""
    email = fields.Email(required=True, error_messages={
        'required': 'Email is required',
        'invalid': 'Invalid email format'
    })
    password = fields.Str(required=True, validate=validate_password)
    full_name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    phone_number = fields.Str(allow_none=True, validate=validate_phone)
    role = fields.Str(allow_none=True, validate=validate.OneOf(['user', 'admin']))

class LoginSchema(Schema):
    """Login request validation"""
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class UpdateProfileSchema(Schema):
    """Profile update validation"""
    full_name = fields.Str(validate=validate.Length(min=2, max=100))
    phone_number = fields.Str(allow_none=True, validate=validate_phone)

class ChangePasswordSchema(Schema):
    """Change password validation"""
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate_password)

class ForgotPasswordSchema(Schema):
    """Forgot password validation"""
    email = fields.Email(required=True)

class ResetPasswordSchema(Schema):
    """Reset password validation"""
    token = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate_password)