from marshmallow import fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from app.models.user import User


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = False
        exclude = ("password_hash",)

    email = fields.Email(required=True)
    password = fields.String(load_only=True, required=True, validate=validate.Length(min=6))
    full_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    phone_number = fields.String(load_default=None)
    role = fields.String(dump_only=True)
    is_active = fields.Boolean(dump_only=True)
    is_verified = fields.Boolean(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
