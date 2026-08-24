from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db
from app.models.notification import Notification, NotificationPreference
from app.schemas.notification_schema import NotificationPreferenceSchema, NotificationSchema

notifications_bp = Blueprint("notifications", __name__)
_schema = NotificationSchema()
_many_schema = NotificationSchema(many=True)
_pref_schema = NotificationPreferenceSchema()


def _uid():
    return int(get_jwt_identity())


@notifications_bp.route("/", methods=["GET"])
@jwt_required()
def get_notifications():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    unread_only = request.args.get("unread", "false").lower() == "true"

    query = (
        Notification.query.filter_by(user_id=_uid())
        .order_by(Notification.created_at.desc())
    )
    if unread_only:
        query = query.filter_by(read=False)

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify(
        {
            "notifications": _many_schema.dump(paginated.items),
            "pagination": {
                "page": paginated.page,
                "per_page": paginated.per_page,
                "total": paginated.total,
                "pages": paginated.pages,
            },
        }
    ), 200


@notifications_bp.route("/unread-count", methods=["GET"])
@jwt_required()
def get_unread_count():
    count = Notification.query.filter_by(user_id=_uid(), read=False).count()
    return jsonify({"unread_count": count}), 200


@notifications_bp.route("/<int:notification_id>/read", methods=["PUT"])
@jwt_required()
def mark_as_read(notification_id):
    notif = Notification.query.filter_by(id=notification_id, user_id=_uid()).first_or_404()
    notif.read = True
    db.session.commit()
    return jsonify({"notification": _schema.dump(notif)}), 200


@notifications_bp.route("/read-all", methods=["PUT"])
@jwt_required()
def mark_all_as_read():
    Notification.query.filter_by(user_id=_uid(), read=False).update({"read": True})
    db.session.commit()
    return jsonify({"message": "All notifications marked as read"}), 200


@notifications_bp.route("/preferences", methods=["GET"])
@jwt_required()
def get_preferences():
    prefs = NotificationPreference.query.filter_by(user_id=_uid()).first()
    if not prefs:
        prefs = NotificationPreference(user_id=_uid())
        db.session.add(prefs)
        db.session.commit()
    return jsonify({"preferences": _pref_schema.dump(prefs)}), 200


@notifications_bp.route("/preferences", methods=["PUT"])
@jwt_required()
def update_preferences():
    prefs = NotificationPreference.query.filter_by(user_id=_uid()).first()
    if not prefs:
        prefs = NotificationPreference(user_id=_uid())
        db.session.add(prefs)

    data = request.get_json() or {}
    for field in ("email_enabled", "sms_enabled", "push_enabled"):
        if field in data:
            setattr(prefs, field, bool(data[field]))

    db.session.commit()
    return jsonify({"preferences": _pref_schema.dump(prefs)}), 200


@notifications_bp.route("/test-email", methods=["POST"])
@jwt_required()
def test_email():
    from app.models.user import User
    from app.services.notification_service import send_email

    user = User.query.get_or_404(_uid())
    sent = send_email(user, "Ajali Test Email", "<p>Your email notifications are working!</p>")
    return jsonify({"sent": sent}), 200


@notifications_bp.route("/test-sms", methods=["POST"])
@jwt_required()
def test_sms():
    from app.models.user import User
    from app.services.notification_service import send_sms

    user = User.query.get_or_404(_uid())
    sent = send_sms(user, "Ajali test: Your SMS notifications are working!")
    return jsonify({"sent": sent}), 200


@notifications_bp.route("/<int:notification_id>", methods=["DELETE"])
@jwt_required()
def delete_notification(notification_id):
    notif = Notification.query.filter_by(id=notification_id, user_id=_uid()).first_or_404()
    db.session.delete(notif)
    db.session.commit()
    return jsonify({"message": "Notification deleted"}), 200


@notifications_bp.route("/all", methods=["DELETE"])
@jwt_required()
def delete_all_notifications():
    Notification.query.filter_by(user_id=_uid()).delete()
    db.session.commit()
    return jsonify({"message": "All notifications deleted"}), 200
