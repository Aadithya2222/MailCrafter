import logging
from typing import Optional
from datetime import datetime

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class RecipientResolver:
    """Service for resolving recipient names to email addresses using DynamoDB."""

    def __init__(self):
        self.table_name = "mailcrafter-contacts"

        self.dynamodb = boto3.resource(
            "dynamodb",
            region_name="ap-south-1"
        )

        self.table = self.dynamodb.Table(self.table_name)

    async def get_all_contacts(self):
        """Get all contacts."""
        response = self.table.scan()

        items = response.get("Items", [])

        return sorted(
            items,
            key=lambda x: x.get("name", "").lower()
        )

    async def get_contact_by_email(self, email: str):
        """Get contact by email."""
        response = self.table.get_item(
            Key={
                "email": email.lower()
            }
        )

        return response.get("Item")

    async def delete_contact(self, email: str):
        """Delete contact."""
        self.table.delete_item(
            Key={
                "email": email.lower()
            }
        )

        return True

    async def add_contact(self, name: str, email: str):
        """Add or update contact."""

        self.table.put_item(
            Item={
                "email": email.lower(),
                "name": name.strip(),
                "createdAt": datetime.utcnow().isoformat()
            }
        )

        logger.info(f"Added contact: {name} -> {email}")

        return True

    async def resolve(
        self,
        recipient_name: Optional[str],
        transcribed_text: Optional[str] = None
    ) -> Optional[str]:
        """
        Resolve recipient name to email address.
        """

        if not recipient_name:
            recipient_name = self._extract_name_from_text(transcribed_text)

        if not recipient_name:
            return None

        response = self.table.scan()

        contacts = response.get("Items", [])

        for contact in contacts:
            if contact.get("name", "").lower() == recipient_name.lower():
                return contact.get("email")

        for contact in contacts:
            if recipient_name.lower() in contact.get("name", "").lower():
                return contact.get("email")

        return None

    def _extract_name_from_text(
        self,
        text: Optional[str]
    ) -> Optional[str]:

        if not text:
            return None

        import re

        patterns = [
            r"(?:hi|hello|hey|dear)\s+([A-Z][a-z]+)",
            r"([A-Z][a-z]+\s+[A-Z][a-z]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)

            if match:
                return match.group(1)

        return None