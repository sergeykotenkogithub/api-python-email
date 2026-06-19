"""
Custom validators module.

This module contains custom validation functions for various data types.
"""

import re
from typing import Optional


def validate_phone_number(phone: str) -> bool:
    """Validate phone number format."""
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Check length
    if len(cleaned) < 10 or len(cleaned) > 15:
        return False
    
    # Check if starts with + or digit
    if not (cleaned.startswith('+') or cleaned[0].isdigit()):
        return False
    
    return True


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS and injection attacks."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove script tags and their content
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove javascript: protocol
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    
    # Remove on* event handlers
    text = re.sub(r'\s+on\w+\s*=\s*["\'][^"\']*["\']', '', text, flags=re.IGNORECASE)
    
    # Trim whitespace
    text = text.strip()
    
    return text


def validate_name(name: str) -> bool:
    """Validate name contains only allowed characters."""
    # Allow letters (including Cyrillic), spaces, hyphens, and apostrophes
    pattern = r"^[a-zA-Zа-яА-ЯёЁ\s\-']+$"
    return bool(re.match(pattern, name))


def extract_email_domain(email: str) -> Optional[str]:
    """Extract domain from email address."""
    try:
        return email.split('@')[1]
    except (IndexError, AttributeError):
        return None


def is_disposable_email(email: str) -> bool:
    """Check if email is from a disposable email service."""
    disposable_domains = [
        'tempmail.com', 'throwaway.email', 'guerrillamail.com',
        'mailinator.com', 'yopmail.com', '10minutemail.com',
        'trashmail.com', 'fakeinbox.com', 'sharklasers.com'
    ]
    
    domain = extract_email_domain(email)
    if domain:
        return domain.lower() in disposable_domains
    return False


def validate_comment_length(comment: str, min_length: int = 10, max_length: int = 1000) -> tuple[bool, str]:
    """Validate comment length and return status with message."""
    if len(comment) < min_length:
        return False, f"Comment must be at least {min_length} characters long"
    
    if len(comment) > max_length:
        return False, f"Comment must not exceed {max_length} characters"
    
    return True, "Valid"


def contains_suspicious_patterns(text: str) -> bool:
    """Check if text contains suspicious patterns (potential spam)."""
    suspicious_patterns = [
        r'(?i)(buy now|click here|free money|limited time|act now)',
        r'(?i)(viagra|casino|lottery|winner|prize)',
        r'(?i)(http[s]?://.*\.[a-z]{2,}.*http[s]?://)',  # Multiple URLs
        r'(.)\1{10,}',  # Repeated characters
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, text):
            return True
    
    return False