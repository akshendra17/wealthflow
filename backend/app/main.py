"""WealthFlow API — FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api.router import api_router
from app.config import settings
from app.core.exceptions import AppError
from app.db.base import Base
from app.db.session import engine

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Import all models so they register with Base.metadata
from app.db.models import *  # noqa: F401, F403

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables. Shutdown: dispose engine."""
    logger.info("starting_up", app=settings.app_name)

    # Create tables (in dev; use Alembic migrations in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("database_ready")
    yield

    # Shutdown
    await engine.dispose()
    logger.info("shutdown_complete")


app = FastAPI(
    title=settings.app_name,
    description="Monthly expenses dashboard — upload statements, categorize, and track trends.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Attach rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


# Global exception handler for domain errors
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    status_map = {
        "NOT_FOUND": 404,
        "DUPLICATE": 409,
        "VALIDATION_ERROR": 422,
        "PARSING_ERROR": 422,
        "UNSUPPORTED_FORMAT": 415,
        "FORBIDDEN": 403,
        "UNAUTHORIZED": 401,
    }
    return JSONResponse(
        status_code=status_map.get(exc.code, 500),
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": getattr(exc, "errors", None),
            }
        },
    )


# Include all API routes
app.include_router(api_router)


@app.get("/")
async def root():
    """Root endpoint — redirects to docs."""
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "docs": "/docs",
    }
