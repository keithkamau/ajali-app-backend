from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import limiter
from app.models.user import User

def role_required(role):
    """Decorator to check user role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if user.role != role:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator to check if user is admin"""
    return role_required('admin')(f)

def rate_limit(limit_string):
    """Custom rate limit decorator"""
    def decorator(f):
        return limiter.limit(limit_string)(f)
    return decorator

def validate_json(schema_cls):
    """Decorator to validate JSON request body"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Missing JSON data'}), 400
            
            try:
                validated_data = schema_cls().load(data)
            except Exception as e:
                return jsonify({'error': 'Validation failed', 'details': str(e)}), 400
            
            return f(validated_data, *args, **kwargs)
        return decorated_function
    return decorator