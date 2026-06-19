"""
Main application module.

This module creates and configures the FastAPI application.
"""

import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager

from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.api.routes import contact, health
from app.middleware.error_handler import (
    ErrorHandlerMiddleware,
    validation_exception_handler,
    general_exception_handler,
    value_error_handler
)
from app.middleware.rate_limit import RateLimitMiddleware
from app.utils.logger import setup_logging, get_logger
from app.repositories.rate_limiter import get_rate_limiter

# Setup logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Initialize rate limiter cleanup task
    rate_limiter = get_rate_limiter()
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}")


def create_app() -> FastAPI:
    """Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="""
        # Developer Portfolio API
        
        A comprehensive backend service for developer portfolio landing pages
        with AI-powered message analysis and email notifications.
        
        ## Features
        
        - **Contact Form Processing**: Submit and process contact form data
        - **AI Analysis**: Automatic sentiment analysis and message classification
        - **Email Notifications**: Send notifications to site owner and confirmation to users
        - **Rate Limiting**: Protection against spam and abuse
        - **Health Monitoring**: Check service health and metrics
        
        ## AI Integration
        
        This API uses OpenAI GPT models to:
        - Analyze message sentiment (positive/negative/neutral)
        - Classify messages into categories
        - Generate suggested responses
        
        ## Rate Limiting
        
        API requests are rate limited to prevent abuse:
        - {settings.RATE_LIMIT_REQUESTS} requests per {settings.RATE_LIMIT_WINDOW} seconds per IP
        - Rate limit headers included in responses
        """,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add rate limiting middleware
    app.add_middleware(RateLimitMiddleware)
    
    # Add error handling middleware
    app.add_middleware(ErrorHandlerMiddleware)
    
    # Add exception handlers
    from fastapi.exceptions import RequestValidationError
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValueError, value_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    # Add request timing middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        """Add process time header to responses."""
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    
    # Include routers
    app.include_router(contact.router)
    app.include_router(health.router)
    
    # Root endpoint
    @app.get("/", tags=["Root"])

    @app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/static")
    async def root():
    # Просто возвращаем HTML файл
        return FileResponse("static/test_api.html")
    
    async def root():
        """Root endpoint.
        
        Returns:
            Basic API information
        """
        return {
            "message": f"Welcome to {settings.APP_NAME}",
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "health": "/api/health"
        }
    
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )