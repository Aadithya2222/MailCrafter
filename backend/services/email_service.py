"""
Email sending service using Resend API.
"""

import logging
import requests
from typing import Optional

from config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails using Resend."""

    def __init__(self):
        self.api_key = settings.RESEND_API_KEY
        self.from_email = settings.FROM_EMAIL

        if not self.api_key:
            raise ValueError(
                "RESEND_API_KEY is missing from environment variables."
            )

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None
    ) -> bool:

        sender = from_email or self.from_email

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "from": sender,
            "to": [to_email],
            "subject": subject,
            "text": body
        }

        response = requests.post(
            "https://api.resend.com/emails",
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code in (200, 201):
            logger.info(f"Email sent successfully to {to_email}")
            return True

        logger.error(response.text)

        raise Exception(
            f"Failed to send email: {response.status_code} - {response.text}"
        )