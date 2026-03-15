from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database.connection import initialize_database, close_all_connections
from app.routers import action_items_router, notes_router
from app.schemas.errors import ErrorResponse, ValidationErrorResponse
from app.services.exceptions import AppException


# Configure logging
logging.basicConfig(
    level=settings.logging.level,
    format=settings.logging.format,
    datefmt=settings.logging.date_format,
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment.value}")
    logger.info(f"Debug mode: {settings.debug}")

    # Initialize database
    try:
        initialize_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down application...")
    close_all_connections()
    logger.info("Database connections closed")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    # Create FastAPI app with lifespan
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="API for extracting action items from text notes",
        docs_url=settings.docs_url if settings.debug else None,
        redoc_url=settings.redoc_url if settings.debug else None,
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    # Add request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url.path}")
        response = await call_next(request)
        logger.info(f"Response: {response.status_code}")
        return response

    # Exception handlers
    @app.exception_handler(AppException)
    async def handle_app_exception(request: Request, exc: AppException) -> JSONResponse:
        """Handle custom application exceptions."""
        error_response = ErrorResponse(
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_exception(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors."""
        errors = []
        for error in exc.errors():
            errors.append(
                {
                    "field": " -> ".join(str(loc) for loc in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"],
                }
            )

        error_response = ValidationErrorResponse(
            error_code="VALIDATION_ERROR",
            message="Validation failed",
            details=errors,
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.model_dump(),
        )

    @app.exception_handler(Exception)
    async def handle_generic_exception(request: Request, exc: Exception) -> JSONResponse:
        """Handle all other exceptions."""
        logger.exception(f"Unhandled exception: {exc}")

        error_response = ErrorResponse(
            error_code="INTERNAL_ERROR",
            message="Internal server error",
            details={"exception": str(exc)} if settings.debug else None,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump(),
        )

    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check() -> Dict[str, Any]:
        """Health check endpoint."""
        return {
            "status": "healthy",
            "app": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment.value,
        }

    # Include routers
    app.include_router(notes_router, prefix=settings.api_prefix)
    app.include_router(action_items_router, prefix=settings.api_prefix)

    # Serve frontend
    @app.get("/", tags=["frontend"])
    async def serve_frontend() -> HTMLResponse:
        """Serve the frontend HTML."""
        html_path = Path(__file__).resolve().parents[1] / "frontend" / "index.html"
        html_content = html_path.read_text(encoding="utf-8")
        return HTMLResponse(content=html_content)

    # Mount static files
    static_dir = Path(__file__).resolve().parents[1] / "frontend"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    return app


# Create app instance
app = create_app()
