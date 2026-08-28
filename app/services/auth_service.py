import bcrypt

from app import db
from app.models.user import User


def register_user(email, password, full_name, phone_number=None):
    if User.query.filter_by(email=email).first():
        return None, "Email already registered"

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = User(
        email=email,
        password_hash=password_hash,
        full_name=full_name,
        phone_number=phone_number,
    )
    db.session.add(user)
    db.session.commit()
    return user, None


def login_user(email, password):
    user = User.query.filter_by(email=email, is_active=True).first()
    if not user:
        return None, "Invalid email or password"
    if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        return None, "Invalid email or password"
    return user, None
