"""
API response models.

This module contains Pydantic models for API responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(
        ...,
        description="Overall service status",
        example="healthy"
    )
    
    version: str = Field(
        ...,
        description="API version",
        example="1.0.0"
    )
    
    timestamp: datetime = Field(
        ...,
        description="Current timestamp"
    )
    
    services: Dict[str, str] = Field(
        ...,
        description="Status of individual services"
    )


class MetricsResponse(BaseModel):
    """Metrics response model."""
    
    total_requests: int = Field(
        ...,
        description="Total number of requests",
        example=150
    )
    
    successful_requests: int = Field(
        ...,
        description="Number of successful requests",
        example=142
    )
    
    failed_requests: int = Field(
        ...,
        description="Number of failed requests",
        example=8
    )
    
    requests_today: int = Field(
        ...,
        description="Number of requests today",
        example=12
    )
    
    average_response_time_ms: float = Field(
        ...,
        description="Average response time in milliseconds",
        example=245.0
    )
    
    top_categories: List[Dict[str, Any]] = Field(
        ...,
        description="Top request categories"
    )
    
    sentiment_distribution: Dict[str, int] = Field(
        ...,
        description="Distribution of message sentiments"
    )


class ErrorResponse(BaseModel):
    """Error response model."""
    
    success: bool = Field(
        default=False,
        description="Always false for error responses"
    )
    
    error: str = Field(
        ...,
        description="Error type",
        example="Validation Error"
    )
    
    message: str = Field(
        ...,
        description="Human-readable error message",
        example="Invalid email format"
    )
    
    details: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Detailed error information"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Error timestamp"
    )


class SuccessResponse(BaseModel):
    """Generic success response model."""
    
    success: bool = Field(
        default=True,
        description="Always true for success responses"
    )
    
    message: str = Field(
        ...,
        description="Success message"
    )
    
    data: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional response data"
    )