import json
import pytest
from app import create_app, db
from app.models.user import User, PasswordResetToken

@pytest.fixture
def app():
    """Create test app"""
    app = create_app('app.config.config.TestingConfig')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()

@pytest.fixture
def test_user(app):
    """Create test user"""
    user = User(
        email='test@example.com',
        password='Test@123456',
        full_name='Test User',
        phone_number='0712345678'
    )
    db.session.add(user)
    db.session.commit()
    return user

def test_register_user(client):
    """Test user registration"""
    response = client.post('/api/auth/register', json={
        'email': 'newuser@example.com',
        'password': 'Test@123456',
        'full_name': 'New User',
        'phone_number': '0712345678'
    })
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'User registered successfully'
    assert data['user']['email'] == 'newuser@example.com'

def test_register_duplicate_email(client, test_user):
    """Test registration with duplicate email"""
    response = client.post('/api/auth/register', json={
        'email': 'test@example.com',
        'password': 'Test@123456',
        'full_name': 'Duplicate User'
    })
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'Email already registered'

def test_login_user(client, test_user):
    """Test user login"""
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'Test@123456'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Login successful'
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert data['user']['email'] == 'test@example.com'

def test_login_invalid_password(client, test_user):
    """Test login with invalid password"""
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'WrongPassword123'
    })
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['error'] == 'Invalid email or password'

def test_get_current_user(client, test_user):
    """Test getting current user profile"""
    # Login first to get token
    login_response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'Test@123456'
    })
    token = json.loads(login_response.data)['access_token']
    
    # Get user profile
    response = client.get('/api/auth/me', headers={
        'Authorization': f'Bearer {token}'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['user']['email'] == 'test@example.com'
    assert data['user']['full_name'] == 'Test User'

def test_update_profile(client, test_user):
    """Test updating user profile"""
    # Login first
    login_response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'Test@123456'
    })
    token = json.loads(login_response.data)['access_token']
    
    # Update profile
    response = client.put('/api/auth/me', json={
        'full_name': 'Updated Name',
        'phone_number': '0712345678'
    }, headers={
        'Authorization': f'Bearer {token}'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Profile updated successfully'
    assert data['user']['full_name'] == 'Updated Name'

def test_change_password(client, test_user):
    """Test changing password"""
    # Login first
    login_response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'Test@123456'
    })
    token = json.loads(login_response.data)['access_token']
    
    # Change password
    response = client.post('/api/auth/change-password', json={
        'current_password': 'Test@123456',
        'new_password': 'NewTest@123456'
    }, headers={
        'Authorization': f'Bearer {token}'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Password changed successfully'
    
    # Login with new password
    login_response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'NewTest@123456'
    })
    
    assert login_response.status_code == 200

def test_forgot_password(client, test_user):
    """Test forgot password request"""
    response = client.post('/api/auth/forgot-password', json={
        'email': 'test@example.com'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Password reset email sent'
    assert 'reset_token' in data

def test_reset_password(client, test_user):
    """Test resetting password with token"""
    # Create reset token
    token_response = client.post('/api/auth/forgot-password', json={
        'email': 'test@example.com'
    })
    token = json.loads(token_response.data)['reset_token']
    
    # Reset password
    response = client.post('/api/auth/reset-password', json={
        'token': token,
        'new_password': 'ResetTest@123456'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Password reset successful'
    
    # Login with new password
    login_response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'ResetTest@123456'
    })
    
    assert login_response.status_code == 200

def test_refresh_token(client, test_user):
    """Test refreshing access token"""
    # Login first
    login_response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'Test@123456'
    })
    refresh_token = json.loads(login_response.data)['refresh_token']
    
    # Refresh token
    response = client.post('/api/auth/refresh', headers={
        'Authorization': f'Bearer {refresh_token}'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data