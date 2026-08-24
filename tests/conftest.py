import pytest
from flask_jwt_extended import create_access_token

from app import create_app, db as _db
from app.models.notification import Notification, NotificationPreference
from app.models.user import User


@pytest.fixture(scope="session")
def app():
    application = create_app("testing")
    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(autouse=True)
def clean_db(app):
    yield
    with app.app_context():
        _db.session.query(NotificationPreference).delete()
        _db.session.query(Notification).delete()
        _db.session.query(User).delete()
        _db.session.commit()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    return _db


@pytest.fixture
def sample_user(app, db):
    with app.app_context():
        user = User(
            email="test@example.com",
            password_hash="hashed",
            full_name="Test User",
            phone_number="+254700000000",
        )
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


@pytest.fixture
def other_user(app, db):
    with app.app_context():
        user = User(
            email="other@example.com",
            password_hash="hashed",
            full_name="Other User",
        )
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


@pytest.fixture
def auth_headers(app, sample_user):
    with app.app_context():
        token = create_access_token(identity=str(sample_user.id))
    return {"Authorization": f"Bearer {token}"}
