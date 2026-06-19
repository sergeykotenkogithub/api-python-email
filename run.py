"""
Application runner script.

This script provides a convenient way to run the application.
"""

import uvicorn
from app.config import settings


if __name__ == "__main__":
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Documentation: http://{settings.HOST}:{settings.PORT}/static")
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
        access_log=True
    )