"""
Email sending service using SMTP (Gmail App Password).
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SMTP."""
    
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.gmail_user = settings.GMAIL_USER
        self.gmail_password = settings.GMAIL_APP_PASSWORD
        
        if not self.gmail_user or not self.gmail_password:
            raise ValueError(
                "GMAIL_USER and GMAIL_APP_PASSWORD must be set in environment variables"
            )
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None
    ) -> bool:
        """
        Send email via SMTP using Gmail App Password.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            body: Email body content
            from_email: Sender email (defaults to GMAIL_USER)
        
        Returns:
            True if email sent successfully
        
        Note:
            This method does NOT store the email body content.
        """
        from_email = from_email or self.gmail_user
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.gmail_user, self.gmail_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(from_email, to_email, text)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            logger.debug(f"Subject: {subject}")
            # Note: We intentionally do NOT log the body content
            
            return True
        
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            raise Exception(
                "Failed to authenticate with Gmail. "
                "Please check your GMAIL_USER and GMAIL_APP_PASSWORD."
            )
        
        except smtplib.SMTPRecipientsRefused as e:
            logger.error(f"Recipient refused: {e}")
            raise Exception(f"Invalid recipient email address: {to_email}")
        
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            raise Exception(f"Failed to send email: {str(e)}")
