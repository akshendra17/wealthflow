"""Domain-specific exceptions for WealthFlow."""

from __future__ import annotations


class AppError(Exception):
    """Base application error."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, entity: str, identifier: str):
        super().__init__(f"{entity} '{identifier}' not found", code="NOT_FOUND")


class DuplicateError(AppError):
    def __init__(self, entity: str, field: str, value: str):
        super().__init__(
            f"{entity} with {field} '{value}' already exists",
            code="DUPLICATE",
        )


class ValidationError(AppError):
    def __init__(self, message, errors=None):
        self.errors = errors or []
        super().__init__(message, code="VALIDATION_ERROR")


class ParsingError(AppError):
    """Raised when statement parsing fails."""

    def __init__(self, message: str):
        super().__init__(message, code="PARSING_ERROR")


class UnsupportedFormatError(AppError):
    """Raised when an unsupported file format is uploaded."""

    def __init__(self, file_type: str):
        super().__init__(
            f"Unsupported file format: '{file_type}'. Supported: CSV",
            code="UNSUPPORTED_FORMAT",
        )
