"""
Gemini API service for professional email rewriting and subject generation.
"""
import logging
from typing import Optional

try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("google-genai not installed. Please install it to use Gemini API.")

from backend.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Gemini API for email generation."""
    
    def __init__(self):
        if not GEMINI_AVAILABLE:
            raise ImportError(
                "google-genai package not installed. "
                "Install it with: pip install google-genai"
            )
        
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set in environment variables")

        # Prefer a modern default model; override via env if needed.
        self.model_name = getattr(settings, "GEMINI_MODEL", None) or "gemini-2.5-flash"
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        logger.info(f"Gemini service initialized (model={self.model_name})")
    
    async def rewrite_email(
        self,
        transcribed_text: str,
        recipient_name: Optional[str] = None,
        intent: Optional[str] = None
    ) -> str:
        """
        Use Gemini to rewrite transcribed text into a professional email.
        
        Args:
            transcribed_text: The raw transcribed speech text
            recipient_name: Optional recipient name
            intent: Optional detected intent
        
        Returns:
            Professionally rewritten email body
        """
        prompt = self._build_rewrite_prompt(transcribed_text, recipient_name, intent)
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            rewritten_email = (response.text or "").strip()
            
            logger.info(f"Rewrote email using Gemini ({len(rewritten_email)} chars)")
            return rewritten_email
        
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            raise Exception(f"Failed to rewrite email: {str(e)}")
    
    async def generate_subject(
        self,
        email_body: str,
        recipient_name: Optional[str] = None,
        intent: Optional[str] = None
    ) -> str:
        """
        Generate a professional email subject line using Gemini.
        
        Args:
            email_body: The email body text
            recipient_name: Optional recipient name
            intent: Optional detected intent
        
        Returns:
            Generated subject line
        """
        prompt = self._build_subject_prompt(email_body, recipient_name, intent)
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            subject = (response.text or "").strip()
            
            # Remove quotes if Gemini wrapped the subject
            subject = subject.strip('"').strip("'")
            
            # Limit subject length (email standard is ~78 chars, but we'll use 100)
            if len(subject) > 100:
                subject = subject[:97] + "..."
            
            logger.info(f"Generated subject: {subject}")
            return subject
        
        except Exception as e:
            logger.error(f"Error generating subject: {e}")
            raise Exception(f"Failed to generate subject: {str(e)}")
    
    def _build_rewrite_prompt(
        self,
        transcribed_text: str,
        recipient_name: Optional[str],
        intent: Optional[str]
    ) -> str:
        """Build the prompt for email rewriting."""
        context_parts = []
        
        if recipient_name:
            context_parts.append(f"Recipient: {recipient_name}")
        
        if intent:
            context_parts.append(f"Email type: {intent.replace('_', ' ').title()}")
        
        context = "\n".join(context_parts) if context_parts else "General email"
        
        prompt = f"""You are a professional email writing assistant. Rewrite the following transcribed speech into a clear, professional, and courteous email.

Context:
{context}

Transcribed speech:
"{transcribed_text}"

Instructions:
1. Convert the casual speech into professional email format
2. Maintain the original intent and key information
3. Use appropriate greeting and closing
4. Ensure proper grammar, spelling, and punctuation
5. Keep the tone professional but friendly
6. Do not add information that wasn't in the original transcription
7. Format the email body only (no subject line)

Email body:"""
        
        return prompt
    
    def _build_subject_prompt(
        self,
        email_body: str,
        recipient_name: Optional[str],
        intent: Optional[str]
    ) -> str:
        """Build the prompt for subject line generation."""
        context_parts = []
        
        if recipient_name:
            context_parts.append(f"Recipient: {recipient_name}")
        
        if intent:
            context_parts.append(f"Email type: {intent.replace('_', ' ').title()}")
        
        context = "\n".join(context_parts) if context_parts else "General email"
        
        prompt = f"""Generate a concise, professional email subject line for the following email.

Context:
{context}

Email body:
{email_body}

Instructions:
1. Create a subject line that accurately summarizes the email content
2. Keep it concise (under 10 words if possible)
3. Use professional language
4. Make it specific and actionable if applicable
5. Do not include quotes or "Subject:" prefix
6. Return only the subject line text

Subject line:"""
        
        return prompt
