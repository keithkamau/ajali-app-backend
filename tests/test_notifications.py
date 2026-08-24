import os
from unittest.mock import MagicMock, patch

import pytest

from app.models.notification import Notification, NotificationPreference


# ── Model tests ──────────────────────────────────────────────────────────────


def test_notification_defaults(db, sample_user):
    n = Notification(user_id=sample_user.id, type="status_change", title="T", message="M")
    db.session.add(n)
    db.session.commit()
    assert n.id is not None
    assert n.read is False
    assert n.created_at is not None
    assert n.data is None


def test_preference_defaults(db, sample_user):
    p = NotificationPreference(user_id=sample_user.id)
    db.session.add(p)
    db.session.commit()
    assert p.email_enabled is True
    assert p.sms_enabled is True
    assert p.push_enabled is False


# ── GET /api/notifications/ ───────────────────────────────────────────────────


def test_get_notifications_returns_own(client, db, sample_user, auth_headers):
    db.session.add(Notification(user_id=sample_user.id, type="t", title="Mine", message="m"))
    db.session.commit()

    r = client.get("/api/notifications/", headers=auth_headers)
    assert r.status_code == 200
    data = r.get_json()
    assert len(data["notifications"]) == 1
    assert data["notifications"][0]["title"] == "Mine"


def test_get_notifications_excludes_others(client, db, sample_user, other_user, auth_headers):
    db.session.add(Notification(user_id=other_user.id, type="t", title="Theirs", message="m"))
    db.session.commit()

    r = client.get("/api/notifications/", headers=auth_headers)
    assert r.get_json()["notifications"] == []


def test_get_notifications_unread_filter(client, db, sample_user, auth_headers):
    db.session.add_all([
        Notification(user_id=sample_user.id, type="t", title="Unread", message="m", read=False),
        Notification(user_id=sample_user.id, type="t", title="Read", message="m", read=True),
    ])
    db.session.commit()

    r = client.get("/api/notifications/?unread=true", headers=auth_headers)
    items = r.get_json()["notifications"]
    assert len(items) == 1
    assert items[0]["title"] == "Unread"


# ── GET /api/notifications/unread-count ──────────────────────────────────────


def test_unread_count(client, db, sample_user, auth_headers):
    db.session.add_all([
        Notification(user_id=sample_user.id, type="t", title="A", message="m", read=False),
        Notification(user_id=sample_user.id, type="t", title="B", message="m", read=True),
    ])
    db.session.commit()

    r = client.get("/api/notifications/unread-count", headers=auth_headers)
    assert r.status_code == 200
    assert r.get_json()["unread_count"] == 1


# ── PUT /api/notifications/<id>/read ─────────────────────────────────────────


def test_mark_as_read(client, db, sample_user, auth_headers):
    n = Notification(user_id=sample_user.id, type="t", title="A", message="m")
    db.session.add(n)
    db.session.commit()

    r = client.put(f"/api/notifications/{n.id}/read", headers=auth_headers)
    assert r.status_code == 200
    db.session.refresh(n)
    assert n.read is True


def test_mark_as_read_wrong_user(client, db, other_user, auth_headers):
    n = Notification(user_id=other_user.id, type="t", title="A", message="m")
    db.session.add(n)
    db.session.commit()

    r = client.put(f"/api/notifications/{n.id}/read", headers=auth_headers)
    assert r.status_code == 404


# ── PUT /api/notifications/read-all ──────────────────────────────────────────


def test_mark_all_as_read(client, db, sample_user, auth_headers):
    db.session.add_all([
        Notification(user_id=sample_user.id, type="t", title="A", message="m"),
        Notification(user_id=sample_user.id, type="t", title="B", message="m"),
    ])
    db.session.commit()

    r = client.put("/api/notifications/read-all", headers=auth_headers)
    assert r.status_code == 200
    unread = Notification.query.filter_by(user_id=sample_user.id, read=False).count()
    assert unread == 0


# ── GET/PUT /api/notifications/preferences ───────────────────────────────────


def test_get_preferences_creates_defaults(client, sample_user, auth_headers):
    r = client.get("/api/notifications/preferences", headers=auth_headers)
    assert r.status_code == 200
    p = r.get_json()["preferences"]
    assert p["email_enabled"] is True
    assert p["sms_enabled"] is True
    assert p["push_enabled"] is False


def test_update_preferences(client, sample_user, auth_headers):
    r = client.put(
        "/api/notifications/preferences",
        json={"email_enabled": False, "sms_enabled": False},
        headers=auth_headers,
    )
    assert r.status_code == 200
    p = r.get_json()["preferences"]
    assert p["email_enabled"] is False
    assert p["sms_enabled"] is False


# ── DELETE ────────────────────────────────────────────────────────────────────


def test_delete_notification(client, db, sample_user, auth_headers):
    n = Notification(user_id=sample_user.id, type="t", title="A", message="m")
    db.session.add(n)
    db.session.commit()
    n_id = n.id

    r = client.delete(f"/api/notifications/{n_id}", headers=auth_headers)
    assert r.status_code == 200
    assert db.session.get(Notification, n_id) is None


def test_delete_all_notifications(client, db, sample_user, auth_headers):
    db.session.add_all([
        Notification(user_id=sample_user.id, type="t", title="A", message="m"),
        Notification(user_id=sample_user.id, type="t", title="B", message="m"),
    ])
    db.session.commit()

    r = client.delete("/api/notifications/all", headers=auth_headers)
    assert r.status_code == 200
    assert Notification.query.filter_by(user_id=sample_user.id).count() == 0


# ── Service: email / SMS guards ───────────────────────────────────────────────


def test_send_email_skips_without_key(app, sample_user):
    os.environ.pop("SENDGRID_API_KEY", None)
    from app.services.notification_service import send_email

    with app.app_context():
        result = send_email(sample_user, "Test", "<p>Hi</p>")
    assert result is False


@patch("sendgrid.SendGridAPIClient")
def test_send_email_calls_sendgrid_with_key(mock_cls, app, sample_user):
    os.environ["SENDGRID_API_KEY"] = "test-key"
    mock_instance = MagicMock()
    mock_cls.return_value = mock_instance

    from app.services.notification_service import send_email

    with app.app_context():
        result = send_email(sample_user, "Subj", "<p>Body</p>")

    assert result is True
    mock_instance.send.assert_called_once()
    os.environ.pop("SENDGRID_API_KEY", None)


def test_send_sms_skips_without_key(app, sample_user):
    os.environ.pop("AT_API_KEY", None)
    from app.services.notification_service import send_sms

    with app.app_context():
        result = send_sms(sample_user, "Test SMS")
    assert result is False


def test_send_sms_skips_without_phone(app, db, sample_user):
    os.environ["AT_API_KEY"] = "test-key"
    sample_user.phone_number = None
    db.session.commit()

    from app.services.notification_service import send_sms

    with app.app_context():
        result = send_sms(sample_user, "Test SMS")
    assert result is False
    os.environ.pop("AT_API_KEY", None)
