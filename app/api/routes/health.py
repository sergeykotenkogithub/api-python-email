"""
Health check API routes module.

This module contains API endpoints for health checks and metrics.
"""

from fastapi import APIRouter, Depends, status
from datetime import datetime
from app.models.responses import HealthResponse, MetricsResponse, ErrorResponse, SuccessResponse
from app.services.contact_service import ContactService, get_contact_service
from app.services.ai_service import AIService, get_ai_service
from app.services.email_service import EmailService, get_email_service
from app.utils.logger import get_logger

logger = get_logger("HealthRouter")

router = APIRouter(prefix="/api", tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check the health status of the API and its services",
    responses={
        200: {
            "description": "Service is healthy",
            "model": HealthResponse
        },
        503: {
            "description": "Service is unhealthy",
            "model": HealthResponse
        }
    }
)
async def health_check(
    ai_service: AIService = Depends(get_ai_service),
    email_service: EmailService = Depends(get_email_service)
):
    """Check API health status.
    
    Args:
        ai_service: AI service instance
        email_service: Email service instance
        
    Returns:
        HealthResponse with service status
    """
    try:
        # Check individual services
        ai_health = await ai_service.health_check()
        email_health = await email_service.health_check()
        
        services_status = {
            "api": "up",
            "ai": ai_health.get("status", "unknown"),
            "email": email_health.get("status", "unknown")
        }
        
        # Determine overall status
        overall_status = "healthy"
        if services_status["ai"] not in ["healthy", "not_configured"] or \
           services_status["email"] not in ["healthy", "not_configured"]:
            overall_status = "degraded"
        
        if services_status["ai"] == "unhealthy" and services_status["email"] == "unhealthy":
            overall_status = "unhealthy"
        
        return HealthResponse(
            status=overall_status,
            version="1.0.0",
            timestamp=datetime.utcnow(),
            services=services_status
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return HealthResponse(
            status="unhealthy",
            version="1.0.0",
            timestamp=datetime.utcnow(),
            services={
                "api": "up",
                "ai": "unknown",
                "email": "unknown",
                "error": str(e)
            }
        )


@router.get(
    "/metrics",
    response_model=dict,
    summary="Get metrics",
    description="Get application metrics and statistics",
    responses={
        200: {
            "description": "Application metrics",
            "model": MetricsResponse
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse
        }
    }
)
async def get_metrics(
    contact_service: ContactService = Depends(get_contact_service)
):
    """Get application metrics.
    
    Args:
        contact_service: Contact service instance
        
    Returns:
        Dict containing application metrics
    """
    try:
        metrics = await contact_service.get_metrics()
        
        return {
            "success": True,
            "data": metrics
        }
        
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}", exc_info=True)
        return {
            "success": False,
            "error": "Failed to retrieve metrics",
            "message": str(e)
        }


@router.get(
    "/status",
    response_model=SuccessResponse,
    summary="API Status",
    description="Simple endpoint to check if API is running",
    responses={
        200: {
            "description": "API is running",
            "model": SuccessResponse
        }
    }
)
async def api_status():
    """Simple status endpoint.
    
    Returns:
        SuccessResponse indicating API is running
    """
    return SuccessResponse(
        success=True,
        message="API is running",
        data={
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat()
        }
    )