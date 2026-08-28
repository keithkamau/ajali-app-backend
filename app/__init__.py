from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from .config.config import config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, origins=app.config["CORS_ORIGINS"])

    with app.app_context():
        from .models import notification  # noqa: F401 — ensures models are registered

    from .models import user  # noqa: F401

    from .routes.auth_routes import auth_bp
    from .routes.notification_routes import notifications_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(notifications_bp, url_prefix="/api/notifications")

    return app
