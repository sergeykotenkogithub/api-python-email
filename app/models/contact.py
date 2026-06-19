"""
Contact form models.

This module contains Pydantic models for contact form data validation
and serialization.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re


class ContactForm(BaseModel):
    """Contact form submission model."""
    
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Full name of the person submitting the form",
        example="Иван Иванов"
    )
    
    email: EmailStr = Field(
        ...,
        description="Email address for response",
        example="ivan@example.com"
    )
    
    phone: Optional[str] = Field(
        None,
        description="Phone number in international format",
        example="+7 (999) 123-45-67"
    )
    
    comment: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Message or comment from the user",
        example="Хочу обсудить разработку веб-приложения"
    )
    
    @validator('name')
    def validate_name(cls, v):
        """Validate name contains only letters and spaces."""
        if not re.match(r'^[a-zA-Zа-яА-ЯёЁ\s\-]+$', v):
            raise ValueError('Name must contain only letters, spaces, and hyphens')
        return v.strip()
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number - + at start, then digits only."""
        if v is None:
            return v
        # Check for letters - not allowed
        if re.search(r'[a-zA-Zа-яА-ЯёЁ]', v):
            raise ValueError('Phone number must contain only digits and optional + at the start')
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', v)
        # + must be at the start only
        if '+' in cleaned:
            if cleaned.index('+') != 0:
                raise ValueError('Plus sign must be at the beginning')
            if cleaned.count('+') > 1:
                raise ValueError('Only one plus sign allowed')
        # Check length (10-15 digits, + doesn't count)
        digits_only = re.sub(r'[^\d]', '', cleaned)
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValueError('Phone number must be between 10 and 15 digits')
        return cleaned
    
    @validator('comment')
    def validate_comment(cls, v):
        """Sanitize comment text."""
        # Remove any potential HTML tags
        cleaned = re.sub(r'<[^>]+>', '', v)
        return cleaned.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Иван Иванов",
                "email": "ivan@example.com",
                "phone": "+7 (999) 123-45-67",
                "comment": "Хочу обсудить разработку веб-приложения"
            }
        }


class AIAnalysis(BaseModel):
    """AI analysis results model."""
    
    sentiment: str = Field(
        ...,
        description="Sentiment of the message: positive, negative, or neutral",
        example="positive"
    )
    
    category: str = Field(
        ...,
        description="Category of the inquiry",
        example="project_inquiry"
    )
    
    priority: str = Field(
        default="medium",
        description="Priority level: low, medium, high",
        example="medium"
    )
    
    suggested_response: Optional[str] = Field(
        None,
        description="AI-generated suggested response",
        example="Спасибо за ваш интерес! Я свяжусь с вами в ближайшее время."
    )
    
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score of the AI analysis",
        example=0.85
    )


class ContactResponse(BaseModel):
    """Contact form submission response model."""
    
    success: bool = Field(
        ...,
        description="Whether the submission was successful"
    )
    
    message: str = Field(
        ...,
        description="Response message"
    )
    
    data: Optional[dict] = Field(
        None,
        description="Additional data including AI analysis"
    )


class ContactInDB(BaseModel):
    """Contact form data as stored in database/file."""
    
    id: str = Field(
        ...,
        description="Unique identifier"
    )
    
    name: str = Field(
        ...,
        description="Full name"
    )
    
    email: str = Field(
        ...,
        description="Email address"
    )
    
    phone: Optional[str] = Field(
        None,
        description="Phone number"
    )
    
    comment: str = Field(
        ...,
        description="Message content"
    )
    
    timestamp: datetime = Field(
        ...,
        description="Submission timestamp"
    )
    
    ai_analysis: Optional[AIAnalysis] = Field(
        None,
        description="AI analysis results"
    )
    
    ip_address: Optional[str] = Field(
        None,
        description="IP address of the submitter"
    )