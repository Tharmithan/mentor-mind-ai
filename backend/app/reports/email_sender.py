"""Optional email delivery for reports (Week 7 · Day 4)."""

from __future__ import annotations

import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path


def send_report_email(
    to_email: str,
    subject: str,
    markdown_body: str,
    pdf_path: Path | None = None,
) -> tuple[bool, str]:
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("REPORT_EMAIL_FROM", user or "noreply@mentormind.ai")

    if not host or not user or not password:
        return False, (
            "Email not configured. Set SMTP_HOST, SMTP_USER, and SMTP_PASSWORD in .env"
        )

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    plain = markdown_body.replace("**", "").replace("*", "")
    msg.attach(MIMEText(plain, "plain"))

    if pdf_path and pdf_path.exists():
        with pdf_path.open("rb") as f:
            attachment = MIMEApplication(f.read(), _subtype="pdf")
            attachment.add_header(
                "Content-Disposition", "attachment", filename=pdf_path.name
            )
            msg.attach(attachment)

    try:
        with smtplib.SMTP(host, port, timeout=15) as server:
            server.starttls()
            server.login(user, password)
            server.sendmail(from_email, [to_email], msg.as_string())
        return True, f"Report emailed to {to_email}"
    except Exception as exc:
        return False, f"Email failed: {exc}"
