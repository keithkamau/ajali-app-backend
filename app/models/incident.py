from datetime import datetime, timezone
from enum import Enum

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class IncidentStatus(str, Enum):
	REPORTED = "reported"
	UNDER_REVIEW = "under_review"
	IN_PROGRESS = "in_progress"
	RESOLVED = "resolved"
	REJECTED = "rejected"


class IncidentMediaType(str, Enum):
	IMAGE = "image"
	VIDEO = "video"


class Incident(db.Model):
	__tablename__ = "incidents"

	id = db.Column(db.BigInteger, primary_key=True)
	user_id = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
	title = db.Column(db.String(120), nullable=False)
	description = db.Column(db.Text, nullable=False)
	type = db.Column(db.String(40), nullable=False, index=True)
	location_lat = db.Column(db.Numeric(9, 6), nullable=False)
	location_lng = db.Column(db.Numeric(9, 6), nullable=False)
	location_address = db.Column(db.String(255), nullable=False)
	status = db.Column(db.Enum(IncidentStatus, name="incident_status"), nullable=False, default=IncidentStatus.REPORTED, index=True)
	is_anonymous = db.Column(db.Boolean, nullable=False, default=False)
	created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
	updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

	media = db.relationship("IncidentMedia", back_populates="incident", cascade="all, delete-orphan")
	status_history = db.relationship("IncidentStatusHistory", back_populates="incident", cascade="all, delete-orphan", order_by="IncidentStatusHistory.changed_at.desc()")


class IncidentMedia(db.Model):
	__tablename__ = "incident_media"

	id = db.Column(db.BigInteger, primary_key=True)
	incident_id = db.Column(db.BigInteger, db.ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
	media_type = db.Column(db.Enum(IncidentMediaType, name="incident_media_type"), nullable=False)
	media_url = db.Column(db.Text, nullable=False)
	public_id = db.Column(db.String(255))
	mime_type = db.Column(db.String(100), nullable=False)
	file_size_bytes = db.Column(db.BigInteger, nullable=False)
	uploaded_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

	incident = db.relationship("Incident", back_populates="media")


class IncidentStatusHistory(db.Model):
	__tablename__ = "incident_status_history"

	id = db.Column(db.BigInteger, primary_key=True)
	incident_id = db.Column(db.BigInteger, db.ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
	old_status = db.Column(db.Enum(IncidentStatus, name="incident_status"), nullable=True)
	new_status = db.Column(db.Enum(IncidentStatus, name="incident_status"), nullable=False)
	changed_by = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
	comment = db.Column(db.Text)
	changed_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

	incident = db.relationship("Incident", back_populates="status_history")
