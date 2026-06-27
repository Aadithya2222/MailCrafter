"""
Utility script for managing contacts in the database.
"""
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.recipient_resolver import RecipientResolver


async def add_contact(name: str, email: str):
    """Add a contact to the database."""
    resolver = RecipientResolver()
    success = await resolver.add_contact(name, email)
    if success:
        print(f"✓ Added contact: {name} -> {email}")
    else:
        print(f"✗ Failed to add contact: {name} -> {email}")


async def list_contacts():
    """List all contacts in the database."""
    import sqlite3
    from config import settings
    
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name, email FROM contacts ORDER BY name")
    contacts = cursor.fetchall()
    
    if contacts:
        print("\nContacts:")
        print("-" * 50)
        for name, email in contacts:
            print(f"  {name:30} {email}")
        print("-" * 50)
        print(f"Total: {len(contacts)} contacts")
    else:
        print("No contacts found.")
    
    conn.close()


async def main():
    """Main function for CLI."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m backend.utils.manage_contacts add <name> <email>")
        print("  python -m backend.utils.manage_contacts list")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "add":
        if len(sys.argv) != 4:
            print("Error: 'add' requires name and email")
            print("Usage: python -m backend.utils.manage_contacts add <name> <email>")
            sys.exit(1)
        
        name = sys.argv[2]
        email = sys.argv[3]
        await add_contact(name, email)
    
    elif command == "list":
        await list_contacts()
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
