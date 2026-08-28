from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from marshmallow import ValidationError

from app.schemas.user_schema import UserSchema
from app.services.auth_service import login_user, register_user

auth_bp = Blueprint("auth", __name__)
_schema = UserSchema()


@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = _schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    user, error = register_user(
        email=data["email"],
        password=data["password"],
        full_name=data["full_name"],
        phone_number=data.get("phone_number"),
    )
    if error:
        return jsonify({"error": error}), 409

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    return jsonify({
        "user": _schema.dump(user),
        "access_token": access_token,
        "refresh_token": refresh_token,
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    body = request.get_json() or {}
    email = body.get("email", "").strip()
    password = body.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user, error = login_user(email, password)
    if error:
        return jsonify({"error": error}), 401

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    return jsonify({
        "user": _schema.dump(user),
        "access_token": access_token,
        "refresh_token": refresh_token,
    }), 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({"access_token": access_token}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    from app.models.user import User
    user = User.query.get_or_404(int(get_jwt_identity()))
    return jsonify({"user": _schema.dump(user)}), 200
