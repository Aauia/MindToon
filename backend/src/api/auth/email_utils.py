# email_utils.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

from dotenv import load_dotenv
load_dotenv()

# Logging setup
logger = logging.getLogger(__name__)

# Load email credentials from environment
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")  # Your Gmail or other SMTP email
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  # App password or SMTP password

def send_email(to: str, subject: str, body: str):
    if not SMTP_USER or not SMTP_PASSWORD:
        raise RuntimeError("Missing SMTP credentials in environment variables.")

    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = to
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        logger.info(f"📨 Email sent to {to}")
    except Exception as e:
        logger.error(f"❌ Failed to send email to {to}: {e}")
        raise
