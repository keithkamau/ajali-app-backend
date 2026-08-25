"""
Authentication routes for user registration, login, and profile management
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.services.auth_service import AuthService
from app.schemas.user_schema import (
    RegisterSchema, LoginSchema, UpdateProfileSchema,
    ChangePasswordSchema, ForgotPasswordSchema, ResetPasswordSchema
)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    POST /api/auth/register
    """
    try:
        # Validate request data
        schema = RegisterSchema()
        data = schema.load(request.json)
        
        # Register user
        user = AuthService.register_user(
            email=data['email'],
            password=data['password'],
            full_name=data['full_name'],
            phone_number=data.get('phone_number'),
            role=data.get('role', 'user')
        )
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user and return tokens
    POST /api/auth/login
    """
    try:
        # Validate request data
        schema = LoginSchema()
        data = schema.load(request.json)
        
        # Login user
        access_token, refresh_token, user = AuthService.login_user(
            email=data['email'],
            password=data['password']
        )
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout user
    POST /api/auth/logout
    """
    # JWT tokens are stateless, client should discard tokens
    return jsonify({'message': 'Logout successful'}), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current user profile
    GET /api/auth/me
    """
    try:
        user_id = get_jwt_identity()
        user = AuthService.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Update current user profile
    PUT /api/auth/me
    """
    try:
        user_id = get_jwt_identity()
        schema = UpdateProfileSchema()
        data = schema.load(request.json)
        
        user = AuthService.update_profile(user_id, data)
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    Change user password
    POST /api/auth/change-password
    """
    try:
        user_id = get_jwt_identity()
        schema = ChangePasswordSchema()
        data = schema.load(request.json)
        
        AuthService.change_password(
            user_id=user_id,
            current_password=data['current_password'],
            new_password=data['new_password']
        )
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Request password reset
    POST /api/auth/forgot-password
    """
    try:
        schema = ForgotPasswordSchema()
        data = schema.load(request.json)
        
        token = AuthService.forgot_password(email=data['email'])
        
        # TODO: Send email with reset link
        # For now, return token (in production, send via email)
        return jsonify({
            'message': 'Password reset email sent',
            'reset_token': token  # Remove in production, send via email
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Reset password with token
    POST /api/auth/reset-password
    """
    try:
        schema = ResetPasswordSchema()
        data = schema.load(request.json)
        
        AuthService.reset_password(
            token=data['token'],
            new_password=data['new_password']
        )
        
        return jsonify({'message': 'Password reset successful'}), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """
    Refresh access token
    POST /api/auth/refresh
    """
    try:
        user_id = get_jwt_identity()
        user = AuthService.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Create new access token
        new_access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'role': user.role}
        )
        
        return jsonify({'access_token': new_access_token}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500