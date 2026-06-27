"""
Contacts management routes (metadata-only database: name + email).
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
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
            id=item.get("id"),
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
        id=saved_contact.get("id"),
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

    resolver = RecipientResolver()

    await resolver.delete_contact(contact_id)

    return {
        "message": "Contact deleted"
    }