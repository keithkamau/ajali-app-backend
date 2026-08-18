from marshmallow import Schema, fields, validate, ValidationError
from email_validator import validate_email, EmailNotValidError

def validate_email_format(email):
    """Validate email format using email-validator"""
    try:
        validate_email(email)
    except EmailNotValidError:
        raise ValidationError('Invalid email address')
    return email

class RegisterSchema(Schema):
    """Schema for user registration"""
    email = fields.Email(required=True, validate=validate_email_format)
    password = fields.Str(
        required=True,
        validate=[
            validate.Length(min=8, max=50, error='Password must be between 8 and 50 characters'),
            validate.Regexp(
                r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)',
                error='Password must contain at least one uppercase letter, one lowercase letter, and one number'
            )
        ]
    )
    full_name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    phone_number = fields.Str(validate=validate.Length(max=20))
    
    class Meta:
        ordered = True


class LoginSchema(Schema):
    """Schema for user login"""
    email = fields.Email(required=True, validate=validate_email_format)
    password = fields.Str(required=True)
    
    class Meta:
        ordered = True


class UserResponseSchema(Schema):
    """Schema for user response (excluding sensitive data)"""
    id = fields.Int()
    email = fields.Email()
    full_name = fields.Str()
    phone_number = fields.Str()
    role = fields.Str()
    is_active = fields.Boolean()
    is_verified = fields.Boolean()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    
    class Meta:
        ordered = True


class UpdateProfileSchema(Schema):
    """Schema for profile update"""
    full_name = fields.Str(validate=validate.Length(min=2, max=100))
    phone_number = fields.Str(validate=validate.Length(max=20))
    
    class Meta:
        ordered = True


class ChangePasswordSchema(Schema):
    """Schema for password change"""
    current_password = fields.Str(required=True)
    new_password = fields.Str(
        required=True,
        validate=[
            validate.Length(min=8, max=50),
            validate.Regexp(
                r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)',
                error='Password must contain at least one uppercase letter, one lowercase letter, and one number'
            )
        ]
    )
    
    class Meta:
        ordered = True


class ForgotPasswordSchema(Schema):
    """Schema for forgot password request"""
    email = fields.Email(required=True, validate=validate_email_format)
    
    class Meta:
        ordered = True


class ResetPasswordSchema(Schema):
    """Schema for password reset"""
    token = fields.Str(required=True)
    new_password = fields.Str(
        required=True,
        validate=[
            validate.Length(min=8, max=50),
            validate.Regexp(
                r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)',
                error='Password must contain at least one uppercase letter, one lowercase letter, and one number'
            )
        ]
    )
    
    class Meta:
        ordered = True