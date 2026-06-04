#======================================#
#       core/utils/email.py            #
#======================================#

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.app.config.settings import settings
from backend.app.config.logging import get_logger

logger = get_logger(__name__)

async def send_email(to_email: str, subject: str, body: str, is_html: bool = False) -> None:
    """
    Sends an email using the SMTP settings configured in .env.
    If SMTP settings are not provided, it falls back to logging the email to the console (useful for local dev).
    """
    if not settings.SMTP_HOST or not settings.SMTP_PASSWORD:
        display_body = body if not is_html else "[HTML Email Content Omitted from Logs]"
        logger.warning(f"SMTP is not configured! Mocking email dispatch.\n--- EMAIL TO {to_email} ---\nSUBJECT: {subject}\nBODY:\n{display_body}\n---------------------------")
        return

    import email.utils
    import re
    
    try:
        # Use 'alternative' so email clients know there's a plain text fallback
        msg = MIMEMultipart("alternative") if is_html else MIMEMultipart()
        msg['From'] = settings.SMTP_FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg['Date'] = email.utils.formatdate(localtime=True)
        msg['Message-ID'] = email.utils.make_msgid(domain=settings.SMTP_FROM_EMAIL.split('@')[-1])

        if is_html:
            # Strip HTML tags for the plain text version (spam filters hate HTML-only emails)
            plain_text = re.sub('<[^<]+?>', ' ', body)
            plain_text = re.sub(' +', ' ', plain_text).strip()
            
            msg.attach(MIMEText(plain_text, 'plain'))
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))

        # We use a synchronous SMTP call here. In a highly concurrent production environment, 
        # this should be offloaded to a background task runner like Celery or FastAPI BackgroundTasks.
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_FROM_EMAIL, settings.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email successfully sent to {to_email}")
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        # We don't raise here so it doesn't crash the request if email fails, but you could depending on requirements