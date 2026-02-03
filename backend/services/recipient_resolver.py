"""
Recipient resolver service for looking up email addresses from contacts.
"""
import logging
import sqlite3
import os
from typing import Optional
from pathlib import Path

from backend.config import settings

logger = logging.getLogger(__name__)


class RecipientResolver:
    """Service for resolving recipient names to email addresses."""
    
    def __init__(self):
        self.db_path = self._get_db_path()
        self._ensure_database()
    
    def _get_db_path(self) -> str:
        """Get database path, creating directory if needed."""
        # Handle both relative and absolute paths
        if settings.DATABASE_URL.startswith("sqlite:///"):
            db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        else:
            db_path = settings.DATABASE_URL
        
        # Create directory if it doesn't exist
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        return db_path
    
    def _ensure_database(self):
        """Create contacts table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_name ON contacts(name)
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
    
    async def resolve(
        self,
        recipient_name: Optional[str],
        transcribed_text: Optional[str] = None
    ) -> Optional[str]:
        """
        Resolve recipient name to email address.
        
        Args:
            recipient_name: The recipient name to look up
            transcribed_text: Optional transcribed text for fuzzy matching
        
        Returns:
            Email address if found, None otherwise
        """
        if not recipient_name:
            # Try to extract name from transcribed text
            recipient_name = self._extract_name_from_text(transcribed_text)
        
        if not recipient_name:
            logger.warning("No recipient name provided")
            return None
        
        # Try exact match first
        email = self._lookup_exact(recipient_name)
        if email:
            logger.info(f"Found exact match: {recipient_name} -> {email}")
            return email
        
        # Try fuzzy match
        email = self._lookup_fuzzy(recipient_name)
        if email:
            logger.info(f"Found fuzzy match: {recipient_name} -> {email}")
            return email
        
        logger.warning(f"No email found for recipient: {recipient_name}")
        return None
    
    def _lookup_exact(self, name: str) -> Optional[str]:
        """Look up exact name match."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT email FROM contacts WHERE LOWER(name) = LOWER(?)",
            (name.strip(),)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def _lookup_fuzzy(self, name: str) -> Optional[str]:
        """Look up fuzzy name match (partial)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Try matching first name or last name
        name_parts = name.strip().split()
        if len(name_parts) >= 2:
            first_name = name_parts[0]
            last_name = name_parts[-1]
            
            cursor.execute(
                """
                SELECT email FROM contacts 
                WHERE LOWER(name) LIKE LOWER(?) OR LOWER(name) LIKE LOWER(?)
                LIMIT 1
                """,
                (f"%{first_name}%", f"%{last_name}%")
            )
        else:
            cursor.execute(
                "SELECT email FROM contacts WHERE LOWER(name) LIKE LOWER(?) LIMIT 1",
                (f"%{name.strip()}%",)
            )
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def _extract_name_from_text(self, text: Optional[str]) -> Optional[str]:
        """Extract name from transcribed text if recipient_name not provided."""
        if not text:
            return None
        
        # Simple extraction - look for capitalized words that might be names
        import re
        # Look for patterns like "Hi John" or "Dear Jane"
        patterns = [
            r"(?:hi|hello|hey|dear)\s+([A-Z][a-z]+)",
            r"([A-Z][a-z]+\s+[A-Z][a-z]+)",  # Full name
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    async def add_contact(self, name: str, email: str) -> bool:
        """
        Add a new contact to the database.
        
        Args:
            name: Contact name
            email: Contact email address
        
        Returns:
            True if added successfully
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO contacts (name, email, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                """,
                (name.strip(), email.strip().lower())
            )
            conn.commit()
            logger.info(f"Added contact: {name} -> {email}")
            return True
        
        except sqlite3.IntegrityError:
            # Email already exists, update the name
            cursor.execute(
                """
                UPDATE contacts 
                SET name = ?, updated_at = CURRENT_TIMESTAMP
                WHERE email = ?
                """,
                (name.strip(), email.strip().lower())
            )
            conn.commit()
            logger.info(f"Updated contact: {name} -> {email}")
            return True
        
        except Exception as e:
            logger.error(f"Error adding contact: {e}")
            conn.rollback()
            return False
        
        finally:
            conn.close()
