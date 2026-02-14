"""Custom exception classes, error handlers, and error response models."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from flask import Flask, jsonify
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Error codes & messages
# ---------------------------------------------------------------------------


class ErrorCode(StrEnum):
    """Application error codes."""

    INVALID_REQUEST = "INVALID_REQUEST"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    HTML_REQUIRED = "HTML_REQUIRED"
    INVALID_BASE64 = "INVALID_BASE64"
    HTML_TOO_LARGE = "HTML_TOO_LARGE"
    JAVASCRIPT_DETECTED = "JAVASCRIPT_DETECTED"
    SANITIZATION_FAILED = "SANITIZATION_FAILED"
    RENDER_FAILED = "RENDER_FAILED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    UNSUPPORTED_MEDIA_TYPE = "UNSUPPORTED_MEDIA_TYPE"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    UNAUTHORIZED = "UNAUTHORIZED"


ERROR_MESSAGES: dict[ErrorCode, str] = {
    ErrorCode.INVALID_REQUEST: "The request body is invalid or malformed.",
    ErrorCode.VALIDATION_ERROR: "Request validation failed.",
    ErrorCode.HTML_REQUIRED: "The 'html' field is required in the request body.",
    ErrorCode.INVALID_BASE64: "The 'html' field must be a valid base64-encoded string.",
    ErrorCode.HTML_TOO_LARGE: "The HTML content exceeds the maximum allowed size.",
    ErrorCode.JAVASCRIPT_DETECTED: (
        "JavaScript was detected in the HTML content. JS is not allowed."
    ),
    ErrorCode.SANITIZATION_FAILED: "Failed to sanitize the HTML content.",
    ErrorCode.RENDER_FAILED: "Failed to render the HTML to PDF.",
    ErrorCode.INTERNAL_ERROR: "An unexpected internal error occurred.",
    ErrorCode.UNSUPPORTED_MEDIA_TYPE: "Content-Type must be application/json.",
    ErrorCode.RATE_LIMIT_EXCEEDED: "Too many requests. Please try again later.",
    ErrorCode.UNAUTHORIZED: "Invalid or missing API key.",
}


# ---------------------------------------------------------------------------
# Base exception & concrete subclasses
# ---------------------------------------------------------------------------


@dataclass
class AppError(Exception):
    """Base application error."""

    code: ErrorCode
    message: str | None = None
    status_code: int = 400
    details: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.message is None:
            self.message = ERROR_MESSAGES.get(self.code, "Unknown error.")
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        error_dict: dict[str, Any] = {
            "error": {
                "code": self.code.value,
                "message": self.message,
            }
        }
        if self.details:
            error_dict["error"]["details"] = self.details
        return error_dict


class InvalidRequestError(AppError):
    """Request body is invalid."""

    def __init__(self, message: str | None = None, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            code=ErrorCode.INVALID_REQUEST,
            message=message,
            status_code=400,
            details=details,
        )


class ValidationError(AppError):
    """Pydantic validation failed."""

    def __init__(self, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            code=ErrorCode.VALIDATION_ERROR,
            status_code=422,
            details=details,
        )


class HtmlRequiredError(AppError):
    """HTML field is missing."""

    def __init__(self) -> None:
        super().__init__(code=ErrorCode.HTML_REQUIRED, status_code=400)


class InvalidBase64Error(AppError):
    """Invalid base64 encoding."""

    def __init__(self) -> None:
        super().__init__(code=ErrorCode.INVALID_BASE64, status_code=400)


class HtmlTooLargeError(AppError):
    """HTML content exceeds size limit."""

    def __init__(self, max_size_mb: int) -> None:
        super().__init__(
            code=ErrorCode.HTML_TOO_LARGE,
            status_code=413,
            details={"max_size_mb": max_size_mb},
        )


class JavaScriptDetectedError(AppError):
    """JavaScript detected in HTML."""

    def __init__(self, details: dict[str, Any] | None = None) -> None:
        super().__init__(code=ErrorCode.JAVASCRIPT_DETECTED, status_code=400, details=details)


class SanitizationError(AppError):
    """HTML sanitization failed."""

    def __init__(self, details: dict[str, Any] | None = None) -> None:
        super().__init__(code=ErrorCode.SANITIZATION_FAILED, status_code=400, details=details)


class RenderError(AppError):
    """PDF rendering failed."""

    def __init__(self, details: dict[str, Any] | None = None) -> None:
        super().__init__(code=ErrorCode.RENDER_FAILED, status_code=500, details=details)


class UnsupportedMediaTypeError(AppError):
    """Wrong content type."""

    def __init__(self) -> None:
        super().__init__(code=ErrorCode.UNSUPPORTED_MEDIA_TYPE, status_code=415)


class RateLimitExceededError(AppError):
    """Rate limit exceeded."""

    def __init__(self) -> None:
        super().__init__(code=ErrorCode.RATE_LIMIT_EXCEEDED, status_code=429)


class UnauthorizedError(AppError):
    """Invalid or missing API key."""

    def __init__(self, message: str | None = None) -> None:
        super().__init__(code=ErrorCode.UNAUTHORIZED, message=message, status_code=401)


# ---------------------------------------------------------------------------
# Pydantic models for error responses (used in Swagger / serialization)
# ---------------------------------------------------------------------------


class ErrorDetail(BaseModel):
    """Error detail in API error responses."""

    code: str = Field(..., description="Machine-readable error code.")
    message: str = Field(..., description="Human-readable error message.")
    details: dict[str, object] | None = Field(default=None, description="Additional error details.")


class ErrorResponse(BaseModel):
    """Standard API error response."""

    error: ErrorDetail


# ---------------------------------------------------------------------------
# Flask error handlers
# ---------------------------------------------------------------------------


def register_error_handlers(app: Flask) -> None:
    """Register error handlers on the Flask app."""

    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):  # noqa: ANN202
        logger.warning(
            "Application error: %s - %s",
            error.code.value,
            error.message,
            extra={"error_code": error.code.value, "details": error.details},
        )
        return jsonify(error.to_dict()), error.status_code

    @app.errorhandler(400)
    def handle_bad_request(error):  # noqa: ANN001, ANN202
        logger.warning("Bad request: %s", str(error))
        return jsonify(
            {
                "error": {
                    "code": ErrorCode.INVALID_REQUEST.value,
                    "message": str(error),
                }
            }
        ), 400

    @app.errorhandler(404)
    def handle_not_found(error):  # noqa: ANN001, ANN202
        logger.info("Not found: %s", str(error))
        return jsonify(
            {
                "error": {
                    "code": "NOT_FOUND",
                    "message": "The requested resource was not found.",
                }
            }
        ), 404

    @app.errorhandler(413)
    def handle_request_entity_too_large(error):  # noqa: ANN001, ANN202
        logger.warning("Request entity too large: %s", str(error))
        return jsonify(
            {
                "error": {
                    "code": ErrorCode.HTML_TOO_LARGE.value,
                    "message": ERROR_MESSAGES[ErrorCode.HTML_TOO_LARGE],
                }
            }
        ), 413

    @app.errorhandler(429)
    def handle_rate_limit_exceeded(error):  # noqa: ANN001, ANN202
        logger.warning("Rate limit exceeded: %s", str(error))
        return jsonify(
            {
                "error": {
                    "code": ErrorCode.RATE_LIMIT_EXCEEDED.value,
                    "message": ERROR_MESSAGES[ErrorCode.RATE_LIMIT_EXCEEDED],
                }
            }
        ), 429

    @app.errorhandler(500)
    def handle_internal_error(error):  # noqa: ANN001, ANN202
        logger.exception("Internal server error: %s", str(error))
        return jsonify(
            {
                "error": {
                    "code": ErrorCode.INTERNAL_ERROR.value,
                    "message": ERROR_MESSAGES[ErrorCode.INTERNAL_ERROR],
                }
            }
        ), 500
