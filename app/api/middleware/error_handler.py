"""Error handler middleware for FastAPI."""

from pydantic import ValidationError

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    ConsolidationError,
    DomainError,
    EntityNotFoundError,
    InsufficientDataError,
    ValidationError as DomainValidationError,
)


def domain_exception_handler(request: Request, exc: DomainError) -> JSONResponse:
    """Handle domain exceptions and map them to appropriate HTTP status codes.

    Args:
        request: The FastAPI request object
        exc: The domain exception that was raised

    Returns:
        JSONResponse with appropriate status code and error details
    """

    # Map domain exceptions to HTTP status codes
    status_code_map = {
        DomainValidationError: status.HTTP_400_BAD_REQUEST,
        ConsolidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
        InsufficientDataError: status.HTTP_422_UNPROCESSABLE_ENTITY,
        EntityNotFoundError: status.HTTP_404_NOT_FOUND,
    }

    status_code = status_code_map.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)

    return JSONResponse(
        status_code=status_code,
        content={
            "error": exc.__class__.__name__,
            "message": str(exc),
            "detail": getattr(exc, "detail", None),
        },
    )


def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic validation errors.

    Args:
        request: The FastAPI request object
        exc: The Pydantic validation error

    Returns:
        JSONResponse with 400 status code and validation error details
    """

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "ValidationError",
            "message": "Invalid request data",
            "detail": exc.errors(),
        },
    )
