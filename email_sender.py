"""
Email Sender: Dispatches curated digest via Gmail SMTP with SSL/TLS and MIME Multipart.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Tuple

from config import (
    GMAIL_USER,
    GMAIL_APP_PASSWORD,
    RECIPIENT_EMAIL,
    SMTP_SERVER,
    SMTP_PORT,
    USE_TLS,
    logger
)


def send_email(subject: str, html_content: str, text_content: str, recipient: str = None) -> Tuple[bool, str]:
    """
    Sends an email with both HTML and Plain Text versions via Gmail SMTP.
    Returns (success: bool, status_message: str).
    """
    to_email = recipient or RECIPIENT_EMAIL
    
    # Credentials check
    if not GMAIL_USER or not GMAIL_APP_PASSWORD or GMAIL_APP_PASSWORD == "your_app_password_here":
        err = (
            "Gmail credentials not configured. Please set GMAIL_USER and GMAIL_APP_PASSWORD "
            "in your d:\\Agents\\.env file using a Google App Password (https://myaccount.google.com/apppasswords)."
        )
        logger.error(err)
        return False, err
        
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"CS Research Digest <{GMAIL_USER}>"
        msg["To"] = to_email
        
        # Attach both plain text and html representations
        part_text = MIMEText(text_content, "plain", "utf-8")
        part_html = MIMEText(html_content, "html", "utf-8")
        
        msg.attach(part_text)
        msg.attach(part_html)
        
        logger.info("Connecting to SMTP server %s:%d...", SMTP_SERVER, SMTP_PORT)
        
        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=20) as server:
                server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
                server.sendmail(GMAIL_USER, [to_email], msg.as_string())
        else:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=20) as server:
                if USE_TLS:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
                server.sendmail(GMAIL_USER, [to_email], msg.as_string())
                
        success_msg = f"Successfully delivered email '{subject}' to {to_email}"
        logger.info(success_msg)
        return True, success_msg
        
    except smtplib.SMTPAuthenticationError as e:
        err_msg = f"SMTP Authentication Failed: {e}. Please ensure you are using a 16-character App Password (not your main Google account password)."
        logger.error(err_msg)
        return False, err_msg
    except Exception as e:
        err_msg = f"Failed to send email via SMTP: {str(e)}"
        logger.error(err_msg)
        return False, err_msg
