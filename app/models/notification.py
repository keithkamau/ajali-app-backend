from datetime import datetime
from app import db


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    data = db.Column(db.JSON, nullable=True)
    read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<Notification {self.id} user={self.user_id} type={self.type}>"


class NotificationPreference(db.Model):
    __tablename__ = "notification_preferences"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    email_enabled = db.Column(db.Boolean, default=True, nullable=False)
    sms_enabled = db.Column(db.Boolean, default=True, nullable=False)
    push_enabled = db.Column(db.Boolean, default=False, nullable=False)

    user = db.relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<NotificationPreference user={self.user_id}>"
