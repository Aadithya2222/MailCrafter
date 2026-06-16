"""
Contacts management routes (metadata-only database: name + email).
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import List

from backend.services.recipient_resolver import RecipientResolver

router = APIRouter()


class Contact(BaseModel):
    id: int | None = Field(default=None)
    name: str
    email: EmailStr

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
            }
        }


@router.get("/contacts", response_model=List[Contact])
async def list_contacts() -> List[Contact]:
    """
    List all contacts stored in the metadata database.
    """
    resolver = RecipientResolver()
    import sqlite3

    conn = sqlite3.connect(resolver.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM contacts ORDER BY name")
    rows = cursor.fetchall()
    conn.close()

    return [Contact(id=row[0], name=row[1], email=row[2]) for row in rows]


@router.post("/contacts", response_model=Contact, status_code=201)
async def add_contact(contact: Contact) -> Contact:
    """
    Add or update a contact.

    - If email exists, name is updated.
    - Otherwise, a new contact is created.
    """
    resolver = RecipientResolver()
    success = await resolver.add_contact(contact.name, contact.email)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save contact")

    import sqlite3

    conn = sqlite3.connect(resolver.db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, email FROM contacts WHERE LOWER(email) = LOWER(?)",
        (contact.email,),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=500, detail="Contact saved but could not be read")

    return Contact(id=row[0], name=row[1], email=row[2])


@router.delete("/contacts/{contact_id}", status_code=204)
async def delete_contact(contact_id: int) -> None:
    """
    Delete a contact by id.
    """
    resolver = RecipientResolver()
    import sqlite3

    conn = sqlite3.connect(resolver.db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
    conn.commit()
    conn.close()

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import List

from backend.services.recipient_resolver import RecipientResolver

router = APIRouter()


class Contact(BaseModel):
    id: int | None = None
    name: str
    email: EmailStr

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com"
            }
        }


@router.get("/contacts", response_model=List[Contact])
async def list_contacts():

    resolver = RecipientResolver()

    contacts = await resolver.get_all_contacts()

    return [
        Contact(
            name=item["name"],
            email=item["email"]
        )
        for item in contacts
    ]


@router.post("/contacts", response_model=Contact, status_code=201)
async def add_contact(contact: Contact):

    resolver = RecipientResolver()

    success = await resolver.add_contact(
        contact.name,
        contact.email
    )

    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to save contact"
        )

    saved_contact = await resolver.get_contact_by_email(
        contact.email
    )

    return Contact(
        name=saved_contact["name"],
        email=saved_contact["email"]
    )


@router.delete("/contacts/{email}")
async def delete_contact(email: str):

    resolver = RecipientResolver()

    await resolver.delete_contact(email)

    return {
        "message": "Contact deleted"
    }