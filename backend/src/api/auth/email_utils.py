# email_utils.py

import os
import logging
import requests
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# Logging setup
logger = logging.getLogger(__name__)

# Load Brevo credentials from environment variables
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
BREVO_SENDER_EMAIL = os.getenv("BREVO_SENDER_EMAIL")  # Must be verified in Brevo

def send_email(to: str, subject: str, body: str):
    """
    Sends an email using the Brevo SMTP API.

    Args:
        to (str): The recipient's email address.
        subject (str): The subject of the email.
        body (str): The plain text or HTML body of the email.
    """
    if not BREVO_API_KEY:
        raise RuntimeError("Missing BREVO_API_KEY in environment variables. Please set it.")
    if not BREVO_SENDER_EMAIL:
        raise RuntimeError("Missing BREVO_SENDER_EMAIL in environment variables. Please set it and ensure it's verified in Brevo.")

    try:
        # Prepare request
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "api-key": BREVO_API_KEY,
            "content-type": "application/json"
        }
        data = {
            "sender": {"name": "MindToon", "email": BREVO_SENDER_EMAIL},
            "to": [{"email": to}],
            "subject": subject,
            "htmlContent": f"<html><body>{body}</body></html>",
            "textContent": body  # optional, fallback for non-HTML readers
        }

        # Send the email
        response = requests.post(url, headers=headers, json=data)

        # Log Brevo's response details for debugging
        logger.info(f"📨 Email sent to {to} via Brevo.")
        logger.info(f"Brevo Response Status Code: {response.status_code}")
        if response.status_code not in [200, 201]:
            logger.warning(f"Brevo returned non-200/201 status code. Body: {response.text}")
            raise Exception("Email sending failed")

    except Exception as e:
        logger.error(f"❌ Failed to send email to {to} via Brevo: {e}")
        raise
