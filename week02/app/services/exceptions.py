from __future__ import annotations

from typing import Any, Dict, Optional

from app.schemas.errors import ErrorCodes


class AppException(Exception):
    """Base exception for all application errors."""

    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class NotFoundException(AppException):
    """Exception raised when a resource is not found."""

    def __init__(
        self,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(error_code, message, 404, details)


class ValidationException(AppException):
    """Exception raised for validation errors."""

    def __init__(
        self,
        error_code: str = ErrorCodes.VALIDATION_ERROR,
        message: str = "Validation error",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(error_code, message, 400, details)


class BusinessLogicException(AppException):
    """Exception raised for business logic errors."""

    def __init__(
        self,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(error_code, message, 400, details)


class DatabaseException(AppException):
    """Exception raised for database errors."""

    def __init__(
        self,
        error_code: str = ErrorCodes.DATABASE_ERROR,
        message: str = "Database error",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(error_code, message, 500, details)


class ExternalServiceException(AppException):
    """Exception raised for external service errors."""

    def __init__(
        self,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(error_code, message, 502, details)


class AuthenticationException(AppException):
    """Exception raised for authentication errors."""

    def __init__(
        self,
        error_code: str = ErrorCodes.UNAUTHORIZED,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(error_code, message, 401, details)


class AuthorizationException(AppException):
    """Exception raised for authorization errors."""

    def __init__(
        self,
        error_code: str = ErrorCodes.FORBIDDEN,
        message: str = "Access forbidden",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(error_code, message, 403, details)


# Specific exceptions
class NoteNotFoundException(NotFoundException):
    """Exception raised when a note is not found."""

    def __init__(self, note_id: int):
        super().__init__(
            error_code=ErrorCodes.NOTE_NOT_FOUND,
            message=f"Note with ID {note_id} not found",
            details={"note_id": note_id},
        )


class ActionItemNotFoundException(NotFoundException):
    """Exception raised when an action item is not found."""

    def __init__(self, action_item_id: int):
        super().__init__(
            error_code=ErrorCodes.ACTION_ITEM_NOT_FOUND,
            message=f"Action item with ID {action_item_id} not found",
            details={"action_item_id": action_item_id},
        )


class ExtractionException(ExternalServiceException):
    """Exception raised when action item extraction fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            error_code=ErrorCodes.EXTRACTION_FAILED,
            message=message,
            details=details,
        )


class OllamaServiceException(ExternalServiceException):
    """Exception raised for Ollama service errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            error_code=ErrorCodes.OLLAMA_SERVICE_ERROR,
            message=message,
            details=details,
        )


class OllamaConnectionException(ExternalServiceException):
    """Exception raised for Ollama connection errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            error_code=ErrorCodes.OLLAMA_CONNECTION_ERROR,
            message=message,
            details=details,
        )
