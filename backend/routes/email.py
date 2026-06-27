"""
Email generation and sending routes.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from services.gemini_service import GeminiService
from services.email_service import EmailService
from services.recipient_resolver import RecipientResolver

router = APIRouter()


class EmailRequest(BaseModel):
    """Request model for email generation and sending."""
    transcribed_text: str = Field(..., description="The transcribed speech text")
    recipient_name: Optional[str] = Field(None, description="Recipient name from intent parsing")
    intent: Optional[str] = Field(None, description="Email intent/purpose")
    
    class Config:
        json_schema_extra = {
            "example": {
                "transcribed_text": "Hey John, I wanted to follow up on our meeting yesterday. Can we schedule another call this week?",
                "recipient_name": "John",
                "intent": "follow_up_and_schedule"
            }
        }


class EmailResponse(BaseModel):
    """Response model for email operations."""
    success: bool
    message: str
    email_body: Optional[str] = None
    subject: Optional[str] = None
    recipient_email: Optional[str] = None


class EmailSendRequest(EmailRequest):
    """Request model for sending email (includes generated content)."""
    email_body: str = Field(..., description="The professionally rewritten email body")
    subject: str = Field(..., description="The generated subject line")


@router.post("/email/generate", response_model=EmailResponse)
async def generate_email(request: EmailRequest):
    """
    Generate professional email using Gemini API.
    
    This endpoint:
    1. Uses Gemini to rewrite the transcribed text professionally
    2. Auto-generates a subject line
    3. Returns the generated email (without storing it)
    """
    try:
        gemini_service = GeminiService()
        # Use Gemini to rewrite email professionally
        rewritten_email = await gemini_service.rewrite_email(
            transcribed_text=request.transcribed_text,
            recipient_name=request.recipient_name,
            intent=request.intent
        )
        
        # Generate subject line
        subject = await gemini_service.generate_subject(
            email_body=rewritten_email,
            recipient_name=request.recipient_name,
            intent=request.intent
        )
        
        return EmailResponse(
            success=True,
            message="Email generated successfully",
            email_body=rewritten_email,
            subject=subject,
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating email: {str(e)}"
        )


@router.post("/email/send", response_model=EmailResponse)
async def send_email(request: EmailSendRequest):
    """
    Send email securely via SMTP.
    
    This endpoint:
    1. Resolves recipient email from contacts
    2. Sends email via SMTP
    3. Does NOT store email body content
    """
    try:
        email_service = EmailService()
        recipient_resolver = RecipientResolver()
        # Resolve recipient email
        recipient_email = await recipient_resolver.resolve(
            recipient_name=request.recipient_name,
            transcribed_text=request.transcribed_text
        )
        
        if not recipient_email:
            raise HTTPException(
                status_code=404,
                detail="Recipient email not found. Please add the contact first."
            )
        
        # Send email (without storing body)
        await email_service.send_email(
            to_email=recipient_email,
            subject=request.subject,
            body=request.email_body
        )
        
        return EmailResponse(
            success=True,
            message="Email sent successfully",
            subject=request.subject,
            recipient_email=recipient_email,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error sending email: {str(e)}"
        )


@router.post("/email/process-and-send", response_model=EmailResponse)
async def process_and_send_email(request: EmailRequest):
    """
    Complete flow: Generate email and send in one request.
    
    This is a convenience endpoint that combines:
    1. Email generation (Gemini rewrite + subject)
    2. Recipient resolution
    3. Email sending
    """
    try:
        gemini_service = GeminiService()
        email_service = EmailService()
        recipient_resolver = RecipientResolver()
        # Step 1: Generate email
        rewritten_email = await gemini_service.rewrite_email(
            transcribed_text=request.transcribed_text,
            recipient_name=request.recipient_name,
            intent=request.intent
        )
        
        subject = await gemini_service.generate_subject(
            email_body=rewritten_email,
            recipient_name=request.recipient_name,
            intent=request.intent
        )
        
        # Step 2: Resolve recipient
        recipient_email = await recipient_resolver.resolve(
            recipient_name=request.recipient_name,
            transcribed_text=request.transcribed_text
        )
        
        if not recipient_email:
            raise HTTPException(
                status_code=404,
                detail="Recipient email not found. Please add the contact first."
            )
        
        # Step 3: Send email (without storing body)
        await email_service.send_email(
            to_email=recipient_email,
            subject=subject,
            body=rewritten_email
        )
        
        return EmailResponse(
            success=True,
            message="Email processed and sent successfully",
            subject=subject,
            recipient_email=recipient_email,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing and sending email: {str(e)}"
        )
