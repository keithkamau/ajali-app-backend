import logging
import os

from app import db
from app.models.notification import Notification, NotificationPreference

logger = logging.getLogger(__name__)

_STATUS_LABELS = {
    "draft": "Draft",
    "under_investigation": "Under Investigation",
    "rejected": "Rejected",
    "resolved": "Resolved",
}


def _label(status):
    return _STATUS_LABELS.get(status, status.replace("_", " ").title())


def create_notification(user_id, notification_type, title, message, data=None):
    notif = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        data=data,
    )
    db.session.add(notif)
    db.session.commit()
    return notif


def send_email(user, subject, html_body):
    api_key = os.environ.get("SENDGRID_API_KEY")
    if not api_key:
        logger.warning("SENDGRID_API_KEY not set — skipping email to %s", user.email)
        return False
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail

        from_email = os.environ.get("SENDGRID_FROM_EMAIL", "noreply@ajali.app")
        msg = Mail(
            from_email=from_email,
            to_emails=user.email,
            subject=subject,
            html_content=html_body,
        )
        SendGridAPIClient(api_key).send(msg)
        return True
    except Exception as exc:
        logger.error("SendGrid error for %s: %s", user.email, exc)
        return False


def send_sms(user, message_text):
    api_key = os.environ.get("AT_API_KEY")
    if not api_key:
        logger.warning("AT_API_KEY not set — skipping SMS for user %s", user.id)
        return False
    phone = getattr(user, "phone_number", None)
    if not phone:
        logger.warning("User %s has no phone number — skipping SMS", user.id)
        return False
    try:
        import africastalking

        username = os.environ.get("AT_USERNAME", "sandbox")
        africastalking.initialize(username, api_key)
        africastalking.SMS.send(
            message_text,
            [phone],
            os.environ.get("AT_SENDER_ID", "AJALI"),
        )
        return True
    except Exception as exc:
        logger.error("Africa's Talking error for user %s: %s", user.id, exc)
        return False


def _status_email_html(user, incident_title, old_status, new_status):
    first_name = ((getattr(user, "full_name", "") or "").split() or ["there"])[0]
    old_label = _label(old_status)
    new_label = _label(new_status)
    return f"""
<html>
<body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
  <div style="background:#e53935;padding:20px;border-radius:8px 8px 0 0;">
    <h1 style="color:white;margin:0;font-size:24px;">Ajali!</h1>
    <p style="color:rgba(255,255,255,.85);margin:4px 0 0;font-size:13px;">Smart. Fast. Verified.</p>
  </div>
  <div style="background:#f8f8f8;padding:24px;border-radius:0 0 8px 8px;">
    <p>Hi {first_name},</p>
    <p>Your incident report has been updated.</p>
    <div style="background:white;border-left:4px solid #e53935;padding:16px;margin:16px 0;border-radius:0 4px 4px 0;">
      <p style="margin:0 0 8px;font-weight:bold;">{incident_title}</p>
      <p style="margin:0;color:#555;">
        Status changed from <strong>{old_label}</strong> to <strong>{new_label}</strong>
      </p>
    </div>
    <p>Log in to Ajali to view your report details.</p>
    <p style="color:#999;font-size:12px;margin-top:24px;">
      To manage notification preferences visit your account settings.
    </p>
  </div>
</body>
</html>
"""


def _incident_created_html(user, incident_title):
    first_name = ((getattr(user, "full_name", "") or "").split() or ["there"])[0]
    return f"""
<html>
<body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
  <div style="background:#e53935;padding:20px;border-radius:8px 8px 0 0;">
    <h1 style="color:white;margin:0;font-size:24px;">Ajali!</h1>
    <p style="color:rgba(255,255,255,.85);margin:4px 0 0;font-size:13px;">Smart. Fast. Verified.</p>
  </div>
  <div style="background:#f8f8f8;padding:24px;border-radius:0 0 8px 8px;">
    <p>Hi {first_name},</p>
    <p>Your incident report has been received and is under review.</p>
    <div style="background:white;border-left:4px solid #e53935;padding:16px;margin:16px 0;border-radius:0 4px 4px 0;">
      <p style="margin:0;font-weight:bold;">{incident_title}</p>
    </div>
    <p>We'll notify you as soon as the status changes.</p>
    <p style="color:#999;font-size:12px;margin-top:24px;">
      To manage notification preferences visit your account settings.
    </p>
  </div>
</body>
</html>
"""


def notify_incident_created(incident, user):
    """
    Call after a new incident is persisted to confirm submission to the reporter.

    TM3 integration (add to POST /api/incidents/ after db.session.commit()):
        from app.services.notification_service import notify_incident_created
        notify_incident_created(incident, current_user)
    """
    notif = create_notification(
        user_id=user.id,
        notification_type="incident_created",
        title="Incident Report Received",
        message=f'Your incident "{incident.title}" has been submitted and is under review.',
        data={"incident_id": incident.id},
    )

    prefs = NotificationPreference.query.filter_by(user_id=user.id).first()
    email_ok = prefs.email_enabled if prefs else True

    if email_ok:
        send_email(
            user,
            f'Ajali: Incident "{incident.title}" received',
            _incident_created_html(user, incident.title),
        )

    return notif


def notify_status_change(incident, old_status, new_status):
    """
    Called by the admin status-update endpoint after persisting the new status.

    TM3 integration (add to PUT /api/admin/incidents/<id>/status after saving):
        from app.services.notification_service import notify_status_change
        notify_status_change(incident, old_status, new_status)
    """
    from app.models.user import User

    user = User.query.get(incident.user_id)
    if not user:
        return None

    notif = create_notification(
        user_id=user.id,
        notification_type="status_change",
        title="Incident Status Updated",
        message=(
            f'Your incident "{incident.title}" status changed from '
            f'{_label(old_status)} to {_label(new_status)}.'
        ),
        data={"incident_id": incident.id, "old_status": old_status, "new_status": new_status},
    )

    prefs = NotificationPreference.query.filter_by(user_id=user.id).first()
    email_ok = prefs.email_enabled if prefs else True
    sms_ok = prefs.sms_enabled if prefs else True

    if email_ok:
        send_email(
            user,
            f'Ajali: Incident "{incident.title}" status updated',
            _status_email_html(user, incident.title, old_status, new_status),
        )

    if sms_ok:
        send_sms(user, f'Ajali: Your incident "{incident.title}" is now {_label(new_status)}.')

    return notif
