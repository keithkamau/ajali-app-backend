from marshmallow import Schema, fields


class NotificationSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    type = fields.Str(dump_only=True)
    title = fields.Str(dump_only=True)
    message = fields.Str(dump_only=True)
    data = fields.Dict(dump_only=True, load_default=None)
    read = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class NotificationPreferenceSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    email_enabled = fields.Bool()
    sms_enabled = fields.Bool()
    push_enabled = fields.Bool()
