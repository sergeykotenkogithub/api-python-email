"""
Error handler middleware module.

This module provides global error handling middleware for the application.
"""

import traceback
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
from app.utils.logger import get_logger

logger = get_logger("ErrorHandler")


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Global error handler middleware."""
    
    async def dispatch(self, request: Request, call_next):
        """Process request and handle any errors.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware/endpoint in chain
            
        Returns:
            Response object
        """
        try:
            response = await call_next(request)
            return response
            
        except RequestValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "success": False,
                    "error": "Validation Error",
                    "message": "Invalid request data",
                    "details": e.errors(),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
        except ValueError as e:
            logger.warning(f"Value error: {e}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success": False,
                    "error": "Bad Request",
                    "message": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Unhandled exception: {e}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation exceptions.
    
    Args:
        request: FastAPI request object
        exc: Validation exception
        
    Returns:
        JSONResponse with validation error details
    """
    logger.warning(f"Validation error for {request.url}: {exc}")
    
    # Format validation errors
    error_details = []
    for error in exc.errors():
        error_details.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation Error",
            "message": "Invalid request data",
            "details": error_details,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions.
    
    Args:
        request: FastAPI request object
        exc: Exception
        
    Returns:
        JSONResponse with error details
    """
    logger.error(f"Unhandled exception for {request.url}: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


async def value_error_handler(request: Request, exc: ValueError):
    """Handle value errors.
    
    Args:
        request: FastAPI request object
        exc: ValueError
        
    Returns:
        JSONResponse with error details
    """
    logger.warning(f"Value error for {request.url}: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error": "Bad Request",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


async def rate_limit_exceeded_handler(request: Request, exc: Exception):
    """Handle rate limit exceeded errors.
    
    Args:
        request: FastAPI request object
        exc: Exception
        
    Returns:
        JSONResponse with rate limit error details
    """
    logger.warning(f"Rate limit exceeded for {request.client.host if request.client else 'unknown'}")
    
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "success": False,
            "error": "Rate Limit Exceeded",
            "message": "Too many requests. Please try again later.",
            "retry_after": 3600,  # 1 hour
            "timestamp": datetime.utcnow().isoformat()
        },
        headers={"Retry-After": "3600"}
    )