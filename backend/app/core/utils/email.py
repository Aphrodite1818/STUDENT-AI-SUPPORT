import email.utils
import re

import aiosmtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from backend.app.config.settings import settings
from backend.app.config.logging import get_logger

logger = get_logger(__name__)


async def send_email(
    to_email: str,
    subject: str,
    body: str,
    is_html: bool = False,
) -> bool:
    """
    Send an email asynchronously.

    Returns:
        bool:
            True  -> Email sent successfully
            False -> Email failed to send
    """

    required_settings = [
        settings.SMTP_HOST,
        settings.SMTP_PORT,
        settings.SMTP_PASSWORD,
        settings.SMTP_FROM_EMAIL,
    ]

    if not all(required_settings):
        logger.warning(
            "SMTP configuration incomplete. "
            "Email sending skipped."
        )
        return False

    # ==========================================================
    # Build Message
    # ==========================================================

    msg = (
        MIMEMultipart("alternative")
        if is_html
        else MIMEMultipart()
    )

    msg["From"] = settings.SMTP_FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg["Date"] = email.utils.formatdate(localtime=True)

    msg["Message-ID"] = email.utils.make_msgid(
        domain=settings.SMTP_FROM_EMAIL.split("@")[-1]
    )

    if is_html:
        plain_text = re.sub(r"<[^>]+>", " ", body)
        plain_text = re.sub(r"\s+", " ", plain_text).strip()

        msg.attach(MIMEText(plain_text, "plain"))
        msg.attach(MIMEText(body, "html"))

    else:
        msg.attach(MIMEText(body, "plain"))

    # ==========================================================
    # SMTP Configuration
    # ==========================================================

    use_tls = settings.SMTP_PORT == 465
    start_tls = settings.SMTP_PORT == 587

    smtp = aiosmtplib.SMTP(
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        use_tls=use_tls,
        start_tls=start_tls,
        timeout=15,
    )

    # ==========================================================
    # Send Email
    # ==========================================================

    try:
        await smtp.connect()

        await smtp.login(
            settings.SMTP_FROM_EMAIL,
            settings.SMTP_PASSWORD,
        )

        await smtp.send_message(msg)

        logger.info(
            f"Email successfully sent to {to_email}"
        )

        return True

    except aiosmtplib.SMTPException as e:
        logger.exception(
            f"SMTP error while sending email to "
            f"{to_email}: {str(e)}"
        )
        return False

    except TimeoutError:
        logger.exception(
            f"SMTP timeout while sending email to "
            f"{to_email}"
        )
        return False

    except Exception as e:
        logger.exception(
            f"Unexpected email error for "
            f"{to_email}: {str(e)}"
        )
        return False

    finally:
        try:
            if smtp.is_connected:
                await smtp.quit()
        except Exception:
            pass

