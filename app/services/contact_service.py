"""
Contact Service module.

This module provides business logic for handling contact form submissions,
including validation, AI analysis, email notifications, and data storage.
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from app.models.contact import ContactForm, ContactResponse, AIAnalysis, ContactInDB
from app.services.ai_service import get_ai_service, AIService
from app.services.email_service import get_email_service, EmailService
from app.repositories.file_repository import get_repository, FileRepository
from app.utils.logger import get_logger
from app.utils.validators import sanitize_input, contains_suspicious_patterns

logger = get_logger("ContactService")


class ContactService:
    """Service for handling contact form submissions."""
    
    def __init__(
        self,
        ai_service: AIService = None,
        email_service: EmailService = None,
        repository: FileRepository = None
    ):
        self.ai_service = ai_service or get_ai_service()
        self.email_service = email_service or get_email_service()
        self.repository = repository or get_repository()
    
    async def process_contact_form(
        self,
        contact: ContactForm,
        ip_address: Optional[str] = None
    ) -> ContactResponse:
        """Process a contact form submission.
        
        This method handles the complete flow:
        1. Validate and sanitize input
        2. Check for spam/suspicious content
        3. Perform AI analysis
        4. Save to storage
        5. Send email notifications
        6. Return response
        
        Args:
            contact: Contact form data
            ip_address: IP address of the submitter
            
        Returns:
            ContactResponse with result and AI analysis
        """
        try:
            logger.info(f"Processing contact form from {contact.name} ({contact.email})")
            
            # Step 1: Sanitize input
            contact = self._sanitize_contact(contact)
            
            # Step 2: Check for spam
            if contains_suspicious_patterns(contact.comment):
                logger.warning(f"Suspicious content detected from {contact.email}")
                # Still process but mark as potential spam
            
            # Step 3: Perform AI analysis
            ai_analysis = await self._analyze_message(contact)
            
            # Step 4: Save to storage
            contact_data = contact.dict()
            contact_data["ai_analysis"] = ai_analysis.dict() if ai_analysis else None
            contact_data["ip_address"] = ip_address
            
            contact_id = await self.repository.save_contact(contact_data)
            
            # Step 5: Send email notifications (concurrent)
            email_tasks = [
                self.email_service.send_contact_notification_to_owner(
                    contact=contact,
                    ai_analysis=ai_analysis,
                    contact_id=contact_id
                )
            ]
            
            # Send confirmation to user
            email_tasks.append(
                self.email_service.send_confirmation_to_user(
                    contact=contact,
                    ai_analysis=ai_analysis
                )
            )
            
            # Execute email sends concurrently
            email_results = await asyncio.gather(*email_tasks, return_exceptions=True)
            
            # Log email results
            for i, result in enumerate(email_results):
                if isinstance(result, Exception):
                    logger.error(f"Email task {i} failed: {result}")
                elif result:
                    logger.info(f"Email task {i} completed successfully")
                else:
                    logger.warning(f"Email task {i} returned False")
            
            # Step 6: Return response
            return ContactResponse(
                success=True,
                message="Ваше сообщение успешно отправлено",
                data={
                    "id": contact_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "ai_analysis": ai_analysis.dict() if ai_analysis else None
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to process contact form: {e}", exc_info=True)
            raise
    
    def _sanitize_contact(self, contact: ContactForm) -> ContactForm:
        """Sanitize contact form data."""
        return ContactForm(
            name=sanitize_input(contact.name),
            email=contact.email,
            phone=contact.phone,
            comment=sanitize_input(contact.comment)
        )
    
    async def _analyze_message(
        self,
        contact: ContactForm
    ) -> Optional[AIAnalysis]:
        """Perform AI analysis on the message.
        
        Args:
            contact: Contact form data
            
        Returns:
            AIAnalysis object or None if analysis fails
        """
        try:
            analysis_result = await self.ai_service.analyze_message(
                message=contact.comment,
                sender_name=contact.name
            )
            
            return AIAnalysis(
                sentiment=analysis_result.get("sentiment", "neutral"),
                category=analysis_result.get("category", "other"),
                priority=analysis_result.get("priority", "medium"),
                suggested_response=analysis_result.get("suggested_response"),
                confidence=analysis_result.get("confidence", 0.5)
            )
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            # Return default analysis
            return AIAnalysis(
                sentiment="neutral",
                category="other",
                priority="medium",
                suggested_response="Спасибо за ваше сообщение! Я свяжусь с вами в ближайшее время.",
                confidence=0.0
            )
    
    async def get_contact_by_id(self, contact_id: str) -> Optional[ContactInDB]:
        """Get a contact by ID.
        
        Args:
            contact_id: Unique contact identifier
            
        Returns:
            ContactInDB object or None if not found
        """
        try:
            all_contacts = await self.repository.get_all_contacts()
            
            for contact_data in all_contacts:
                if contact_data.get("id") == contact_id:
                    return ContactInDB(**contact_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get contact by ID {contact_id}: {e}")
            return None
    
    async def get_all_contacts(self) -> list:
        """Get all contacts.
        
        Returns:
            List of ContactInDB objects
        """
        try:
            contacts_data = await self.repository.get_all_contacts()
            return [ContactInDB(**data) for data in contacts_data]
            
        except Exception as e:
            logger.error(f"Failed to get all contacts: {e}")
            return []
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get application metrics.
        
        Returns:
            Dict containing various metrics
        """
        try:
            metrics = await self.repository.get_metrics()
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "requests_today": 0,
                "average_response_time_ms": 0.0,
                "top_categories": [],
                "sentiment_distribution": {},
                "last_updated": datetime.utcnow().isoformat()
            }
    
    async def get_contacts_by_date(self, date_str: str) -> list:
        """Get contacts for a specific date.
        
        Args:
            date_str: Date string in YYYY-MM-DD format
            
        Returns:
            List of ContactInDB objects
        """
        try:
            from datetime import datetime
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            contacts_data = await self.repository.get_contacts_by_date(target_date)
            return [ContactInDB(**data) for data in contacts_data]
            
        except Exception as e:
            logger.error(f"Failed to get contacts for date {date_str}: {e}")
            return []


# Create global contact service instance
contact_service = ContactService()


def get_contact_service() -> ContactService:
    """Get contact service instance."""
    return contact_service