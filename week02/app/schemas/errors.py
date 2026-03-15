from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    error_code: str = Field(
        ...,
        description="Machine-readable error code",
        examples=["NOTE_NOT_FOUND", "VALIDATION_ERROR", "INTERNAL_ERROR"],
    )
    message: str = Field(
        ...,
        description="Human-readable error message",
        examples=["Note with ID 123 not found"],
    )
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error details",
        examples=[{"note_id": 123}],
    )


class ValidationErrorDetail(BaseModel):
    """Schema for validation error details."""

    field: str = Field(
        ...,
        description="Field that failed validation",
        examples=["content"],
    )
    message: str = Field(
        ...,
        description="Validation error message",
        examples=["field required"],
    )
    type: str = Field(
        ...,
        description="Type of validation error",
        examples=["missing"],
    )


class ValidationErrorResponse(ErrorResponse):
    """Schema for validation error response."""

    details: List[ValidationErrorDetail] = Field(
        ...,
        description="List of validation errors",
    )


# Common error codes
class ErrorCodes:
    """Common error codes for the application."""

    # Resource errors
    NOTE_NOT_FOUND = "NOTE_NOT_FOUND"
    ACTION_ITEM_NOT_FOUND = "ACTION_ITEM_NOT_FOUND"

    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    REQUIRED_FIELD_MISSING = "REQUIRED_FIELD_MISSING"
    INVALID_INPUT = "INVALID_INPUT"

    # Business logic errors
    EXTRACTION_FAILED = "EXTRACTION_FAILED"

    # Database errors
    DATABASE_ERROR = "DATABASE_ERROR"

    # External service errors
    OLLAMA_SERVICE_ERROR = "OLLAMA_SERVICE_ERROR"
    OLLAMA_CONNECTION_ERROR = "OLLAMA_CONNECTION_ERROR"

    # Authentication/authorization errors
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"

    # Server errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
