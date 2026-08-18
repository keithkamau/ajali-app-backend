from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required, get_jwt_identity, 
    create_access_token, create_refresh_token,
    get_jwt
)
from app.services.auth_service import AuthService
from app.schemas.user_schema import (
    RegisterSchema, LoginSchema, UpdateProfileSchema,
    ChangePasswordSchema, ForgotPasswordSchema, ResetPasswordSchema,
    UserResponseSchema
)
from app.utils.decorators import validate_json, rate_limit
from app.utils.validators import sanitize_input

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
@validate_json(RegisterSchema)
@rate_limit('5/minute')
def register(data):
    """
    Register a new user
    ---
    Request body: { email, password, full_name, phone_number (optional) }
    """
    try:
        # Sanitize inputs
        email = sanitize_input(data['email'])
        full_name = sanitize_input(data['full_name'])
        phone_number = sanitize_input(data.get('phone_number', ''))
        
        # Create user
        user, error = AuthService.create_user(
            email=email,
            password=data['password'],
            full_name=full_name,
            phone_number=phone_number
        )
        
        if error:
            return jsonify({'error': error}), 400
        
        # Generate tokens
        tokens = AuthService.generate_tokens(user)
        
        # Return user data and tokens
        return jsonify({
            'message': 'Registration successful',
            'user': UserResponseSchema().dump(user),
            'tokens': tokens
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'An error occurred during registration', 'details': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
@validate_json(LoginSchema)
@rate_limit('10/minute')
def login(data):
    """
    Login user
    ---
    Request body: { email, password }
    """
    try:
        # Authenticate user
        user, error = AuthService.authenticate_user(
            email=data['email'],
            password=data['password']
        )
        
        if error:
            return jsonify({'error': error}), 401
        
        # Generate tokens
        tokens = AuthService.generate_tokens(user)
        
        return jsonify({
            'message': 'Login successful',
            'user': UserResponseSchema().dump(user),
            'tokens': tokens
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'An error occurred during login', 'details': str(e)}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token using refresh token"""
    try:
        current_user_id = get_jwt_identity()
        user = AuthService.get_user_by_id(int(current_user_id))
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403
        
        # Create new access token
        new_access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'access_token': new_access_token,
            'token_type': 'bearer'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'An error occurred refreshing token', 'details': str(e)}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout user (client-side token removal)
    Note: This doesn't invalidate the token server-side.
    Client should remove the token from storage.
    """
    return jsonify({'message': 'Logout successful'}), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = AuthService.get_user_by_id(int(current_user_id))
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': UserResponseSchema().dump(user)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'An error occurred', 'details': str(e)}), 500


@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
@validate_json(UpdateProfileSchema)
def update_profile(data):
    """Update current user profile"""
    try:
        current_user_id = get_jwt_identity()
        
        # Sanitize inputs
        if 'full_name' in data:
            data['full_name'] = sanitize_input(data['full_name'])
        if 'phone_number' in data:
            data['phone_number'] = sanitize_input(data['phone_number'])
        
        user, error = AuthService.update_profile(int(current_user_id), data)
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': UserResponseSchema().dump(user)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'An error occurred updating profile', 'details': str(e)}), 500


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
@validate_json(ChangePasswordSchema)
def change_password(data):
    """Change user password"""
    try:
        current_user_id = get_jwt_identity()
        
        success, message = AuthService.change_password(
            user_id=int(current_user_id),
            current_password=data['current_password'],
            new_password=data['new_password']
        )
        
        if not success:
            return jsonify({'error': message}), 400
        
        return jsonify({'message': message}), 200
        
    except Exception as e:
        return jsonify({'error': 'An error occurred changing password', 'details': str(e)}), 500


@auth_bp.route('/forgot-password', methods=['POST'])
@validate_json(ForgotPasswordSchema)
@rate_limit('3/minute')
def forgot_password(data):
    """
    Request password reset
    ---
    Request body: { email }
    """
    try:
        email = sanitize_input(data['email'])
        user = User.query.filter_by(email=email.lower().strip()).first()
        
        if not user:
            # Return success even if user not found (security best practice)
            return jsonify({
                'message': 'If your email exists, you will receive a password reset link'
            }), 200
        
        # TODO: Generate reset token and send email
        # For now, return a placeholder message
        return jsonify({
            'message': 'Password reset link sent to your email'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'An error occurred', 'details': str(e)}), 500


@auth_bp.route('/reset-password', methods=['POST'])
@validate_json(ResetPasswordSchema)
def reset_password(data):
    """
    Reset password with token
    ---
    Request body: { token, new_password }
    """
    try:
        # TODO: Verify reset token and update password
        # For now, return a placeholder
        return jsonify({
            'message': 'Password reset successful'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'An error occurred resetting password', 'details': str(e)}), 500


@auth_bp.route('/deactivate', methods=['POST'])
@jwt_required()
def deactivate_account():
    """Deactivate user account"""
    try:
        current_user_id = get_jwt_identity()
        
        success, message = AuthService.deactivate_user(int(current_user_id))
        
        if not success:
            return jsonify({'error': message}), 400
        
        return jsonify({'message': message}), 200
        
    except Exception as e:
        return jsonify({'error': 'An error occurred deactivating account', 'details': str(e)}), 500