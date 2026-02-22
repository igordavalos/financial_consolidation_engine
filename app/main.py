"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app.api.middleware.error_handler import (
    domain_exception_handler,
    validation_exception_handler,
)
from app.api.v1.endpoints import accounts, data_sources, health, reports, transactions
from app.config import settings
from app.domain.exceptions import DomainError

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(DomainError, domain_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)

# Register routers
app.include_router(health.router)
app.include_router(reports.router, prefix=settings.api_v1_prefix)
app.include_router(accounts.router, prefix=settings.api_v1_prefix)
app.include_router(transactions.router, prefix=settings.api_v1_prefix)
app.include_router(data_sources.router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root() -> dict[str, str]:
    """
    Root endpoint with API information.
    
    Returns:
        dict: Welcome message and documentation link
    """
    return {
        "message": "Financial Consolidation Engine API",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }
