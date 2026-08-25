import secrets
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.models.user import User, PasswordResetToken
from app.utils.validators import is_valid_email, is_valid_password

class AuthService:
    """Authentication service class"""
    
    @staticmethod
    def register_user(email, password, full_name, phone_number=None, role='user'):
        """
        Register a new user
        
        Args:
            email (str): User email
            password (str): User password
            full_name (str): User full name
            phone_number (str, optional): User phone number
            role (str): User role (default: user)
            
        Returns:
            User: Created user object
            
        Raises:
            ValueError: If email already exists or validation fails
        """
        # Validate email
        if not is_valid_email(email):
            raise ValueError('Invalid email format')
        
        # Check if email already exists
        if User.query.filter_by(email=email.lower().strip()).first():
            raise ValueError('Email already registered')
        
        # Validate password
        if not is_valid_password(password):
            raise ValueError('Password must be at least 8 characters with uppercase, lowercase, number, and special character')
        
        # Create user
        user = User(
            email=email,
            password=password,
            full_name=full_name,
            phone_number=phone_number,
            role=role
        )
        
        db.session.add(user)
        db.session.commit()
        
        return user
    
    @staticmethod
    def login_user(email, password):
        """
        Authenticate user and generate tokens
        
        Args:
            email (str): User email
            password (str): User password
            
        Returns:
            tuple: (access_token, refresh_token, user)
            
        Raises:
            ValueError: If credentials are invalid
        """
        # Find user by email
        user = User.query.filter_by(email=email.lower().strip()).first()
        
        if not user:
            raise ValueError('Invalid email or password')
        
        if not user.is_active:
            raise ValueError('Account is deactivated')
        
        # Verify password
        if not user.check_password(password):
            raise ValueError('Invalid email or password')
        
        # Create tokens
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'role': user.role}
        )
        refresh_token = create_refresh_token(
            identity=str(user.id),
            additional_claims={'role': user.role}
        )
        
        return access_token, refresh_token, user
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        return User.query.get(user_id)
    
    @staticmethod
    def update_profile(user_id, data):
        """
        Update user profile
        
        Args:
            user_id (UUID): User ID
            data (dict): Profile data to update
            
        Returns:
            User: Updated user object
            
        Raises:
            ValueError: If validation fails
        """
        user = User.query.get(user_id)
        
        if not user:
            raise ValueError('User not found')
        
        # Update fields
        if 'full_name' in data:
            user.full_name = data['full_name'].strip()
        if 'phone_number' in data:
            user.phone_number = data['phone_number']
        
        db.session.commit()
        return user
    
    @staticmethod
    def change_password(user_id, current_password, new_password):
        """
        Change user password
        
        Args:
            user_id (UUID): User ID
            current_password (str): Current password
            new_password (str): New password
            
        Raises:
            ValueError: If current password is incorrect or validation fails
        """
        user = User.query.get(user_id)
        
        if not user:
            raise ValueError('User not found')
        
        # Verify current password
        if not user.check_password(current_password):
            raise ValueError('Current password is incorrect')
        
        # Validate new password
        if not is_valid_password(new_password):
            raise ValueError('Password must be at least 8 characters with uppercase, lowercase, number, and special character')
        
        # Update password
        user.set_password(new_password)
        db.session.commit()
    
    @staticmethod
    def forgot_password(email):
        """
        Generate password reset token
        
        Args:
            email (str): User email
            
        Returns:
            str: Reset token
            
        Raises:
            ValueError: If user not found
        """
        user = User.query.filter_by(email=email.lower().strip()).first()
        
        if not user:
            raise ValueError('User not found')
        
        # Delete existing tokens
        PasswordResetToken.query.filter_by(user_id=user.id).delete()
        
        # Generate new token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        
        db.session.add(reset_token)
        db.session.commit()
        
        return token
    
    @staticmethod
    def reset_password(token, new_password):
        """
        Reset password using token
        
        Args:
            token (str): Reset token
            new_password (str): New password
            
        Raises:
            ValueError: If token is invalid or expired
        """
        reset_token = PasswordResetToken.query.filter_by(token=token).first()
        
        if not reset_token:
            raise ValueError('Invalid reset token')
        
        if not reset_token.is_valid():
            raise ValueError('Reset token expired or already used')
        
        # Get user
        user = User.query.get(reset_token.user_id)
        
        if not user:
            raise ValueError('User not found')
        
        # Validate new password
        if not is_valid_password(new_password):
            raise ValueError('Password must be at least 8 characters with uppercase, lowercase, number, and special character')
        
        # Update password
        user.set_password(new_password)
        
        # Mark token as used
        reset_token.mark_used()
        
        db.session.commit()