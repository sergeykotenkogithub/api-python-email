"""
Contact API routes module.

This module contains API endpoints for contact form handling.
"""

from fastapi import APIRouter, Depends, Request, HTTPException, status
from typing import Optional
from datetime import datetime
from app.models.contact import ContactForm, ContactResponse
from app.models.responses import ErrorResponse, SuccessResponse
from app.services.contact_service import ContactService, get_contact_service
from app.api.deps import get_client_ip
from app.utils.logger import get_logger

logger = get_logger("ContactRouter")

router = APIRouter(prefix="/api", tags=["Contact"])


@router.post(
    "/contact",
    response_model=ContactResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit contact form",
    description="""
    Submit a contact form with your details and message.
    
    The message will be analyzed by AI for sentiment and classification,
    and email notifications will be sent to both the site owner and the user.
    
    Rate limiting applies: maximum 5 requests per hour per IP address.
    """,
    responses={
        200: {
            "description": "Contact form submitted successfully",
            "model": ContactResponse
        },
        422: {
            "description": "Validation error",
            "model": ErrorResponse
        },
        429: {
            "description": "Rate limit exceeded",
            "model": ErrorResponse
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse
        }
    }
)
async def submit_contact_form(
    contact: ContactForm,
    request: Request,
    contact_service: ContactService = Depends(get_contact_service)
):
    """Process contact form submission.
    
    Args:
        contact: Contact form data
        request: FastAPI request object
        contact_service: Contact service instance
        
    Returns:
        ContactResponse with submission result and AI analysis
        
    Raises:
        HTTPException: If processing fails
    """
    client_ip = get_client_ip(request)
    logger.info(f"Contact form submission from IP: {client_ip}")
    
    try:
        # Process the contact form
        response = await contact_service.process_contact_form(
            contact=contact,
            ip_address=client_ip
        )
        
        logger.info(f"Contact form processed successfully for {contact.email}")
        return response
        
    except ValueError as e:
        logger.warning(f"Validation error for contact form from {contact.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "success": False,
                "error": "Validation Error",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Failed to process contact form: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "message": "An unexpected error occurred. Please try again later."
            }
        )


@router.get(
    "/contacts",
    response_model=dict,
    summary="Get all contacts",
    description="Retrieve all contact form submissions (for admin purposes)",
    responses={
        200: {
            "description": "List of all contacts"
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse
        }
    }
)
async def get_all_contacts(
    contact_service: ContactService = Depends(get_contact_service)
):
    """Get all contact submissions.
    
    Args:
        contact_service: Contact service instance
        
    Returns:
        Dict containing list of contacts
    """
    try:
        contacts = await contact_service.get_all_contacts()
        return {
            "success": True,
            "data": {
                "contacts": [contact.dict() for contact in contacts],
                "total": len(contacts)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get contacts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "message": "Failed to retrieve contacts"
            }
        )


@router.get(
    "/contacts/{contact_id}",
    response_model=dict,
    summary="Get contact by ID",
    description="Retrieve a specific contact submission by its ID",
    responses={
        200: {
            "description": "Contact details"
        },
        404: {
            "description": "Contact not found",
            "model": ErrorResponse
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse
        }
    }
)
async def get_contact_by_id(
    contact_id: str,
    contact_service: ContactService = Depends(get_contact_service)
):
    """Get contact by ID.
    
    Args:
        contact_id: Unique contact identifier
        contact_service: Contact service instance
        
    Returns:
        Dict containing contact details
        
    Raises:
        HTTPException: If contact not found
    """
    try:
        contact = await contact_service.get_contact_by_id(contact_id)
        
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": "Not Found",
                    "message": f"Contact with ID {contact_id} not found"
                }
            )
        
        return {
            "success": True,
            "data": contact.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get contact {contact_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal Server Error",
                "message": "Failed to retrieve contact"
            }
        )