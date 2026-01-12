import logging
import os
import smtplib
from datetime import datetime
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO
from typing import Optional

import qrcode

from app import models


class EmailSettings:
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        from_email: str,
        from_name: str,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.from_name = from_name


def load_email_settings() -> Optional[EmailSettings]:
    host = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    port = int(os.getenv("EMAIL_PORT", "587"))
    username = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")
    from_email = os.getenv("EMAIL_FROM", username or "")
    from_name = os.getenv("EMAIL_FROM_NAME", "Events ENPC")

    if not username or not password or not from_email:
        return None

    return EmailSettings(
        host=host,
        port=port,
        username=username,
        password=password,
        from_email=from_email,
        from_name=from_name,
    )


def _format_event_date(value: datetime) -> str:
    return value.strftime("%d/%m/%Y %H:%M")


def _build_qr_image_bytes(token: str) -> bytes:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(token)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def send_participant_qr_email(
    event: models.Event,
    participant: models.Participant,
    qr_token: str,
) -> None:
    settings = load_email_settings()
    if settings is None or not participant.email:
        logging.warning(
            "Email ignored (missing settings or participant email) event_id=%s participant_id=%s",
            getattr(event, "id", None),
            getattr(participant, "id", None),
        )
        return

    date_str = _format_event_date(event.date)
    full_name = f"{participant.first_name} {participant.last_name}".strip()
    subject = f"{event.name} - {date_str} - {full_name}"

    text_body = (
        f"Bonjour {full_name},\n\n"
        f"Voici votre QR code pour l'evenement \"{event.name}\" "
        f"le {date_str} a {event.location}.\n\n"
        "Merci et a bientot."
    )

    html_body = f"""
    <html>
      <body>
        <p>Bonjour {full_name},</p>
        <p>
          Voici votre QR code pour l'evenement
          "<strong>{event.name}</strong>" le {date_str} a {event.location}.
        </p>
        <p>Le QR code est en piece jointe (qr_code.png).</p>
        <p>Merci et a bientot.</p>
      </body>
    </html>
    """

    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"] = f"{settings.from_name} <{settings.from_email}>"
    msg["To"] = participant.email

    alternative = MIMEMultipart("alternative")
    alternative.attach(MIMEText(text_body, "plain", "utf-8"))
    alternative.attach(MIMEText(html_body, "html", "utf-8"))
    msg.attach(alternative)

    qr_bytes = _build_qr_image_bytes(qr_token)
    attachment = MIMEImage(qr_bytes, _subtype="png")
    attachment.add_header("Content-Disposition", "attachment", filename="qr_code.png")
    msg.attach(attachment)

    try:
        with smtplib.SMTP(settings.host, settings.port) as server:
            server.starttls()
            server.login(settings.username, settings.password)
            server.send_message(msg)
        logging.info(
            "Email sent event_id=%s participant_id=%s to=%s",
            getattr(event, "id", None),
            getattr(participant, "id", None),
            participant.email,
        )
    except Exception as exc:
        logging.exception(
            "Email send failed event_id=%s participant_id=%s to=%s error=%s",
            getattr(event, "id", None),
            getattr(participant, "id", None),
            participant.email,
            exc,
        )
