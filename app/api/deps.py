"""
API dependencies module.

This module provides dependency injection functions for API routes.
"""

from fastapi import Request
from typing import Optional
from app.services.contact_service import get_contact_service, ContactService
from app.services.ai_service import get_ai_service, AIService
from app.services.email_service import get_email_service, EmailService
from app.repositories.rate_limiter import get_rate_limiter, RateLimiter
from app.repositories.file_repository import get_repository, FileRepository


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Client IP address as string
    """
    # Check for forwarded IP (behind proxy/load balancer)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    # Check for real IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to direct client IP
    if request.client:
        return request.client.host
    
    return "unknown"


def get_contact_service_dep() -> ContactService:
    """Dependency for contact service."""
    return get_contact_service()


def get_ai_service_dep() -> AIService:
    """Dependency for AI service."""
    return get_ai_service()


def get_email_service_dep() -> EmailService:
    """Dependency for email service."""
    return get_email_service()


def get_rate_limiter_dep() -> RateLimiter:
    """Dependency for rate limiter."""
    return get_rate_limiter()


def get_repository_dep() -> FileRepository:
    """Dependency for file repository."""
    return get_repository()