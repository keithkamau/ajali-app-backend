from marshmallow import Schema, fields, validate


INCIDENT_TYPES = ("fire", "medical", "crime", "accident", "flood", "other")
INCIDENT_STATUSES = ("reported", "under_review", "in_progress", "resolved", "rejected")


class IncidentMediaSchema(Schema):
	id = fields.Integer(dump_only=True)
	media_type = fields.String(required=True, validate=validate.OneOf(("image", "video")))
	media_url = fields.Url(required=True)
	public_id = fields.String(allow_none=True)
	mime_type = fields.String(required=True)
	file_size_bytes = fields.Integer(required=True, validate=validate.Range(min=1))
	uploaded_at = fields.DateTime(dump_only=True)


class IncidentStatusHistorySchema(Schema):
	id = fields.Integer(dump_only=True)
	old_status = fields.String(allow_none=True, validate=validate.OneOf(INCIDENT_STATUSES))
	new_status = fields.String(required=True, validate=validate.OneOf(INCIDENT_STATUSES))
	changed_by = fields.Integer(dump_only=True)
	comment = fields.String(allow_none=True)
	changed_at = fields.DateTime(dump_only=True)


class IncidentCreateSchema(Schema):
	title = fields.String(required=True, validate=validate.Length(min=1, max=120))
	description = fields.String(required=True, validate=validate.Length(min=1))
	type = fields.String(required=True, validate=validate.OneOf(INCIDENT_TYPES))
	location_lat = fields.Decimal(required=True, as_string=False, validate=validate.Range(min=-90, max=90))
	location_lng = fields.Decimal(required=True, as_string=False, validate=validate.Range(min=-180, max=180))
	location_address = fields.String(required=True, validate=validate.Length(min=1, max=255))
	is_anonymous = fields.Boolean(load_default=False)


class IncidentUpdateSchema(Schema):
	title = fields.String(validate=validate.Length(min=1, max=120))
	description = fields.String(validate=validate.Length(min=1))
	type = fields.String(validate=validate.OneOf(INCIDENT_TYPES))
	location_lat = fields.Decimal(as_string=False, validate=validate.Range(min=-90, max=90))
	location_lng = fields.Decimal(as_string=False, validate=validate.Range(min=-180, max=180))
	location_address = fields.String(validate=validate.Length(min=1, max=255))
	is_anonymous = fields.Boolean()


class IncidentSchema(Schema):
	id = fields.Integer(dump_only=True)
	user_id = fields.Integer(dump_only=True)
	title = fields.String(required=True)
	description = fields.String(required=True)
	type = fields.String(required=True)
	location_lat = fields.Decimal(as_string=False)
	location_lng = fields.Decimal(as_string=False)
	location_address = fields.String(required=True)
	status = fields.String(dump_only=True)
	is_anonymous = fields.Boolean()
	created_at = fields.DateTime(dump_only=True)
	updated_at = fields.DateTime(dump_only=True)
	media = fields.List(fields.Nested(IncidentMediaSchema), dump_only=True)
	status_history = fields.List(fields.Nested(IncidentStatusHistorySchema), dump_only=True)
