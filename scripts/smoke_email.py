"""
Verify SendGrid delivery without needing JWT or auth routes.

Usage:
    python scripts/smoke_email.py
    python scripts/smoke_email.py recipient@example.com
"""
import os
import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from app import create_app
from app.services.notification_service import send_email


class _User:
    def __init__(self, email, full_name):
        self.email = email
        self.full_name = full_name


def main():
    recipient = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("SENDGRID_FROM_EMAIL")
    if not recipient:
        print("Usage: python scripts/smoke_email.py recipient@example.com")
        sys.exit(1)

    app = create_app()
    with app.app_context():
        user = _User(email=recipient, full_name="Ajali Test")
        ok = send_email(
            user,
            subject="Ajali — SendGrid smoke test",
            html_body="""
<html>
<body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
  <div style="background:#e53935;padding:20px;border-radius:8px 8px 0 0;">
    <h1 style="color:white;margin:0;font-size:24px;">Ajali!</h1>
  </div>
  <div style="background:#f8f8f8;padding:24px;border-radius:0 0 8px 8px;">
    <p>SendGrid is wired up and delivering. You're good to go.</p>
  </div>
</body>
</html>
""",
        )
        if ok:
            print(f"✓ Email sent to {recipient}")
        else:
            print("✗ Send failed — check SENDGRID_API_KEY and verified sender.")
            sys.exit(1)


if __name__ == "__main__":
    main()
