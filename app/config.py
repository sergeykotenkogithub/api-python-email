"""
Application configuration module.
"""

import os
from dotenv import load_dotenv

load_dotenv()

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Developer Portfolio API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS - Use specific origins instead of wildcard
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:5501",
        "http://127.0.0.1:5502",
        "https://api-python-email.onrender.com",
        "https://*.onrender.com",
        "file://",
        "null"
    ]
    
    # Email Settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = ""
    EMAIL_TO: str = ""
    
    # AI Settings
    # Provider values: "openai" | "groq"
    AI_PROVIDER: str = "groq"
    # Keys MUST come from .env / environment. Do not commit secrets to the repo.
    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    # Default model per provider; can be overridden via env
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 1000
    RATE_LIMIT_WINDOW: int = 3600
    
    # Data Storage
    DATA_DIR: str = "./data"
    LOGS_DIR: str = "./logs"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
