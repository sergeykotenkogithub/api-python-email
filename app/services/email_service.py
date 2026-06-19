"""
Email Service module.

This module provides email sending functionality for contact form notifications.
"""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.config import settings
from app.utils.logger import get_logger
from app.models.contact import ContactForm, AIAnalysis

logger = get_logger("EmailService")


class EmailService:
    """Email service for sending notifications."""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.email_from = settings.EMAIL_FROM
        self.email_to = settings.EMAIL_TO
        self.is_configured = all([self.smtp_user, self.smtp_password, self.email_from, self.email_to])
    
    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str, 
        text_content: Optional[str] = None
    ) -> bool:
        """Send an email."""
        if not self.is_configured:
            logger.warning("Email service not configured, skipping email send")
            return False
        
        try:
            message = MIMEMultipart("alternative")
            message["From"] = self.email_from
            message["To"] = to_email
            message["Subject"] = subject
            
            if text_content:
                message.attach(MIMEText(text_content, "plain", "utf-8"))
            
            message.attach(MIMEText(html_content, "html", "utf-8"))
            
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                use_tls=True
            )
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    async def send_contact_notification_to_owner(
        self, 
        contact: ContactForm, 
        ai_analysis: Optional[AIAnalysis] = None,
        contact_id: Optional[str] = None
    ) -> bool:
        """Send contact form notification to site owner."""
        subject = f"New message from {contact.name}"
        
        html_content = f"""
        <html>
        <body>
            <h2>New Contact Form Submission</h2>
            <p><strong>Name:</strong> {contact.name}</p>
            <p><strong>Email:</strong> {contact.email}</p>
            {f'<p><strong>Phone:</strong> {contact.phone}</p>' if contact.phone else ''}
            <p><strong>Message:</strong></p>
            <blockquote>{contact.comment}</blockquote>
            {self._build_ai_analysis_section(ai_analysis) if ai_analysis else ''}
        </body>
        </html>
        """
        
        text_content = f"New message from {contact.name}\n\n"
        text_content += f"Email: {contact.email}\n"
        if contact.phone:
            text_content += f"Phone: {contact.phone}\n"
        text_content += f"\nMessage:\n{contact.comment}\n"
        
        return await self.send_email(
            to_email=self.email_to,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_confirmation_to_user(
        self, 
        contact: ContactForm, 
        ai_analysis: Optional[AIAnalysis] = None
    ) -> bool:
        """Send confirmation email to user."""
        subject = "Your message has been received"
        
        html_content = f"""
        <html>
        <body>
            <h2>Thank you for your message!</h2>
            <p>Hello {contact.name},</p>
            <p>I have received your message and will respond as soon as possible.</p>
            <h3>Your message:</h3>
            <blockquote>{contact.comment}</blockquote>
            {f'<p><strong>AI Response:</strong> {ai_analysis.suggested_response}</p>' if ai_analysis and ai_analysis.suggested_response else ''}
            <p>Best regards,<br>Developer</p>
        </body>
        </html>
        """
        
        text_content = f"Hello {contact.name}!\n\n"
        text_content += "I have received your message and will respond as soon as possible.\n\n"
        text_content += f"Your message:\n{contact.comment}\n\n"
        if ai_analysis and ai_analysis.suggested_response:
            text_content += f"AI Response:\n{ai_analysis.suggested_response}\n\n"
        text_content += "Best regards,\nDeveloper"
        
        return await self.send_email(
            to_email=contact.email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    def _build_ai_analysis_section(self, ai_analysis: AIAnalysis) -> str:
        """Build HTML section for AI analysis."""
        return f"""
        <div style="background: #e7f3ff; padding: 15px; border-radius: 5px; margin-top: 20px;">
            <h3>AI Analysis</h3>
            <p><strong>Sentiment:</strong> {ai_analysis.sentiment}</p>
            <p><strong>Category:</strong> {ai_analysis.category}</p>
            <p><strong>Priority:</strong> {ai_analysis.priority}</p>
            <p><strong>Confidence:</strong> {ai_analysis.confidence:.0%}</p>
            {f'<p><strong>Suggested Response:</strong> {ai_analysis.suggested_response}</p>' if ai_analysis.suggested_response else ''}
        </div>
        """
    
    async def health_check(self) -> dict:
        """Check email service health."""
        if not self.is_configured:
            return {
                "status": "not_configured",
                "reason": "SMTP settings not configured"
            }
        
        try:
            await aiosmtplib.connect(
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_tls=True
            )
            return {
                "status": "healthy",
                "smtp_host": self.smtp_host,
                "smtp_port": self.smtp_port
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


email_service = EmailService()


def get_email_service() -> EmailService:
    """Get email service instance."""
    return email_service