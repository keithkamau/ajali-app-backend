from datetime import datetime
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.models.user import User
import bcrypt

class AuthService:
    """Service for authentication operations"""
    
    @staticmethod
    def hash_password(password):
        """Hash password using bcrypt"""
        return generate_password_hash(password)
    
    @staticmethod
    def verify_password(password, password_hash):
        """Verify password against hash"""
        return check_password_hash(password_hash, password)
    
    @staticmethod
    def create_user(email, password, full_name, phone_number=None, role='user'):
        """Create a new user"""
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return None, 'User with this email already exists'
        
        # Hash password
        hashed_password = AuthService.hash_password(password)
        
        # Create user
        user = User(
            email=email.lower().strip(),
            password_hash=hashed_password,
            full_name=full_name.strip(),
            phone_number=phone_number.strip() if phone_number else None,
            role=role
        )
        
        db.session.add(user)
        db.session.commit()
        
        return user, None
    
    @staticmethod
    def authenticate_user(email, password):
        """Authenticate user by email and password"""
        user = User.query.filter_by(email=email.lower().strip()).first()
        
        if not user:
            return None, 'Invalid email or password'
        
        if not user.is_active:
            return None, 'Account is deactivated'
        
        if not AuthService.verify_password(password, user.password_hash):
            return None, 'Invalid email or password'
        
        return user, None
    
    @staticmethod
    def generate_tokens(user):
        """Generate JWT access and refresh tokens"""
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer'
        }
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        return User.query.get(user_id)
    
    @staticmethod
    def update_profile(user_id, data):
        """Update user profile"""
        user = User.query.get(user_id)
        if not user:
            return None, 'User not found'
        
        if 'full_name' in data:
            user.full_name = data['full_name'].strip()
        
        if 'phone_number' in data:
            user.phone_number = data['phone_number'].strip()
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return user, None
    
    @staticmethod
    def change_password(user_id, current_password, new_password):
        """Change user password"""
        user = User.query.get(user_id)
        if not user:
            return False, 'User not found'
        
        # Verify current password
        if not AuthService.verify_password(current_password, user.password_hash):
            return False, 'Current password is incorrect'
        
        # Update password
        user.password_hash = AuthService.hash_password(new_password)
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return True, 'Password updated successfully'
    
    @staticmethod
    def deactivate_user(user_id):
        """Deactivate user account"""
        user = User.query.get(user_id)
        if not user:
            return False, 'User not found'
        
        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return True, 'Account deactivated successfully'