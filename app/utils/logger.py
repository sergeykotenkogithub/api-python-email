"""
Logging configuration module.

This module sets up structured logging with file rotation
and different log levels for various components.
"""

import sys
from pathlib import Path
from loguru import logger
from app.config import settings


def setup_logging():
    """Configure application logging."""
    
    # Create logs directory if it doesn't exist
    logs_dir = Path(settings.LOGS_DIR)
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Remove default logger
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG" if settings.DEBUG else "INFO",
        colorize=True
    )
    
    # Add file handler for all logs
    logger.add(
        str(logs_dir / "app.log"),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="INFO",
        rotation="1 day",
        retention="30 days",
        compression="zip"
    )
    
    # Add file handler for errors only
    logger.add(
        str(logs_dir / "errors.log"),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="1 day",
        retention="90 days",
        compression="zip"
    )
    
    # Add file handler for API requests
    logger.add(
        str(logs_dir / "requests.log"),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        level="INFO",
        filter=lambda record: "api_request" in record["extra"],
        rotation="1 day",
        retention="30 days",
        compression="zip"
    )
    
    logger.info("Logging configured successfully")
    return logger


def get_logger(name: str = None):
    """Get a logger instance with optional name context."""
    if name:
        return logger.bind(name=name)
    return logger


def log_request(method: str, path: str, status_code: int, response_time: float, ip: str = None):
    """Log API request details."""
    logger.bind(api_request=True).info(
        f"{method} {path} - {status_code} - {response_time:.2f}ms - IP: {ip}"
    )


def log_error(error: Exception, context: str = None):
    """Log error with context."""
    if context:
        logger.error(f"{context}: {str(error)}", exc_info=True)
    else:
        logger.error(str(error), exc_info=True)


def log_ai_request(prompt: str, response: str, model: str, tokens_used: int = None):
    """Log AI API request."""
    logger.bind(ai_request=True).info(
        f"AI Request - Model: {model}, Tokens: {tokens_used}, Prompt: {prompt[:100]}..."
    )