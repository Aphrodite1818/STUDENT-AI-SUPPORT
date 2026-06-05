import aiosmtplib
import email.utils
import re

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from backend.app.config.settings import settings
from backend.app.config.logging import get_logger

logger = get_logger(__name__)


async def send_email(
    to_email: str,
    subject: str,
    body: str,
    is_html: bool = False
) -> None:

    if not all([settings.SMTP_HOST, settings.SMTP_PASSWORD, settings.SMTP_FROM_EMAIL]):
        display_body = body if not is_html else "[HTML Email Content Omitted from Logs]"
        logger.warning(
            f"SMTP not configured or sender email missing.\n"
            f"TO: {to_email}\nSUBJECT: {subject}\nBODY:\n{display_body}"
        )
        return

    msg = MIMEMultipart("alternative") if is_html else MIMEMultipart()

    msg["From"] = settings.SMTP_FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg["Date"] = email.utils.formatdate(localtime=True)
    msg["Message-ID"] = email.utils.make_msgid(
        domain=settings.SMTP_FROM_EMAIL.split("@")[-1]
    )

    if is_html:
        plain_text = re.sub(r"<[^>]+>", " ", body)
        plain_text = re.sub(r" {2,}", " ", plain_text).strip()
        msg.attach(MIMEText(plain_text, "plain"))
        msg.attach(MIMEText(body, "html"))
    else:
        msg.attach(MIMEText(body, "plain"))

    smtp = aiosmtplib.SMTP(
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        start_tls=True,
    )

    try:
        await smtp.connect()
        await smtp.login(settings.SMTP_FROM_EMAIL, settings.SMTP_PASSWORD)
        await smtp.send_message(msg)
        logger.info(f"Email successfully sent to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        raise
    finally:
        try:
            await smtp.quit()
        except Exception:
            pass
