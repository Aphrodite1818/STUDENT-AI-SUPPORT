#======================================#
#       core/utils/email.py            #
#======================================#

import smtplib
import email.utils
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi.concurrency import run_in_threadpool
from backend.app.config.settings import settings
from backend.app.config.logging import get_logger

logger = get_logger(__name__)


def send_email_sync(to_email: str, subject: str, body: str, is_html: bool = False) -> None:
    """
    Synchronous function that encapsulates all smtplib operations.
    This function is intended to be executed in a thread pool to prevent event-loop blocking.
    """
    if not settings.SMTP_HOST or not settings.SMTP_PASSWORD:
        display_body = body if not is_html else "[HTML Email Content Omitted from Logs]"
        logger.warning(f"SMTP is not configured! Mocking email dispatch.\n--- EMAIL TO {to_email} ---\nSUBJECT: {subject}\nBODY:\n{display_body}\n---------------------------")
        return

    try:
        msg = MIMEMultipart("alternative") if is_html else MIMEMultipart()
        msg['From'] = settings.SMTP_FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg['Date'] = email.utils.formatdate(localtime=True)
        msg['Message-ID'] = email.utils.make_msgid(domain=settings.SMTP_FROM_EMAIL.split('@')[-1])

        if is_html:
            plain_text = re.sub('<[^<]+?>', ' ', body)
            plain_text = re.sub(' +', ' ', plain_text).strip()

            msg.attach(MIMEText(plain_text, 'plain'))
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_FROM_EMAIL, settings.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()

        logger.info(f"Email successfully sent to {to_email}")

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")


async def send_email(to_email: str, subject: str, body: str, is_html: bool = False) -> None:
    """
    Async wrapper that offloads the synchronous SMTP operations to a thread pool
    using FastAPI's run_in_threadpool, preventing event-loop blocking.
    Does not interact with smtplib directly.
    """
    try:
        await run_in_threadpool(send_email_sync, to_email, subject, body, is_html)
    except Exception as e:
        logger.error(f"Unexpected error while offloading email task for {to_email}: {str(e)}")