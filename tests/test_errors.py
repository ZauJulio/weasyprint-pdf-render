"""Tests for custom exception classes and error handlers."""

from __future__ import annotations

from typing import Any

from app.errors import (
    AppError,
    ErrorCode,
    HtmlRequiredError,
    HtmlTooLargeError,
    InvalidBase64Error,
    InvalidRequestError,
    JavaScriptDetectedError,
    RateLimitExceededError,
    RenderError,
    SanitizationError,
    UnsupportedMediaTypeError,
    ValidationError,
)


class TestAppError:
    """Tests for the base AppError class."""

    def test_default_message_from_code(self) -> None:
        error = AppError(code=ErrorCode.INVALID_REQUEST)
        assert error.message == "The request body is invalid or malformed."

    def test_custom_message_overrides(self) -> None:
        error = AppError(code=ErrorCode.INVALID_REQUEST, message="Custom message")
        assert error.message == "Custom message"

    def test_to_dict_without_details(self) -> None:
        error = AppError(code=ErrorCode.HTML_REQUIRED)
        result = error.to_dict()
        assert result["error"]["code"] == "HTML_REQUIRED"
        assert "details" not in result["error"]

    def test_to_dict_with_details(self) -> None:
        details: dict[str, Any] = {"key": "value"}
        error = AppError(code=ErrorCode.RENDER_FAILED, details=details)
        result = error.to_dict()
        assert result["error"]["details"] == {"key": "value"}

    def test_str_representation(self) -> None:
        error = AppError(code=ErrorCode.INTERNAL_ERROR)
        assert str(error) == "An unexpected internal error occurred."


class TestConcreteErrors:
    """Tests for specific error subclasses."""

    def test_invalid_request_error(self) -> None:
        error = InvalidRequestError()
        assert error.code == ErrorCode.INVALID_REQUEST
        assert error.status_code == 400

    def test_invalid_request_error_with_details(self) -> None:
        error = InvalidRequestError(details={"reason": "bad"})
        assert error.details == {"reason": "bad"}

    def test_validation_error(self) -> None:
        error = ValidationError(details={"errors": [{"loc": ["html"], "msg": "required"}]})
        assert error.code == ErrorCode.VALIDATION_ERROR
        assert error.status_code == 422
        assert error.details is not None

    def test_html_required_error(self) -> None:
        error = HtmlRequiredError()
        assert error.code == ErrorCode.HTML_REQUIRED
        assert error.status_code == 400

    def test_invalid_base64_error(self) -> None:
        error = InvalidBase64Error()
        assert error.code == ErrorCode.INVALID_BASE64
        assert error.status_code == 400

    def test_html_too_large_error(self) -> None:
        error = HtmlTooLargeError(max_size_mb=10)
        assert error.code == ErrorCode.HTML_TOO_LARGE
        assert error.status_code == 413
        assert error.details == {"max_size_mb": 10}

    def test_javascript_detected_error(self) -> None:
        error = JavaScriptDetectedError(details={"detections": ["script tag"]})
        assert error.code == ErrorCode.JAVASCRIPT_DETECTED
        assert error.status_code == 400

    def test_sanitization_error(self) -> None:
        error = SanitizationError(details={"reason": "failed"})
        assert error.code == ErrorCode.SANITIZATION_FAILED
        assert error.status_code == 400
        assert error.details == {"reason": "failed"}

    def test_render_error(self) -> None:
        error = RenderError(details={"reason": "crash"})
        assert error.code == ErrorCode.RENDER_FAILED
        assert error.status_code == 500
        assert error.details == {"reason": "crash"}

    def test_unsupported_media_type_error(self) -> None:
        error = UnsupportedMediaTypeError()
        assert error.code == ErrorCode.UNSUPPORTED_MEDIA_TYPE
        assert error.status_code == 415

    def test_rate_limit_exceeded_error(self) -> None:
        error = RateLimitExceededError()
        assert error.code == ErrorCode.RATE_LIMIT_EXCEEDED
        assert error.status_code == 429


class TestErrorHandlers:
    """Tests for Flask error handlers."""

    def test_app_error_handler(self, client) -> None:
        """AppError handler is tested implicitly by route tests, verify structure."""
        response = client.post(
            "/api/v1/render",
            data="not json",
            content_type="text/plain",
        )
        assert response.status_code == 415
        data = response.get_json()
        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]

    def test_404_handler(self, client) -> None:
        response = client.get("/nonexistent-path")
        assert response.status_code == 404
        data = response.get_json()
        assert data["error"]["code"] == "NOT_FOUND"

    def test_413_handler(self, client) -> None:
        """Test the 413 handler via the HTML too large route path."""
        import base64

        large_html = "<html><body>" + "x" * (2 * 1024 * 1024) + "</body></html>"
        encoded = base64.b64encode(large_html.encode()).decode()
        response = client.post(
            "/api/v1/render",
            json={"html": encoded},
            content_type="application/json",
        )
        assert response.status_code == 413
        data = response.get_json()
        assert data["error"]["code"] == "HTML_TOO_LARGE"

    def test_500_handler(self, app, client) -> None:
        """Test the 500 internal server error handler."""
        from unittest.mock import patch

        # Disable exception propagation so Flask uses its error handler
        app.config["TESTING"] = False
        app.config["PROPAGATE_EXCEPTIONS"] = False

        with patch(
            "app.features.render.routes.validate_and_sanitize",
            side_effect=RuntimeError("unexpected crash"),
        ):
            response = client.post(
                "/api/v1/render",
                json={"html": "dGVzdA=="},
                content_type="application/json",
            )
            assert response.status_code == 500
            data = response.get_json()
            assert data["error"]["code"] == "INTERNAL_ERROR"

    def test_400_handler_native_flask(self, app, client) -> None:
        """Test native Flask 400 bad request handler (not AppError)."""
        from flask import abort

        @app.route("/test-bad-request")
        def trigger_bad_request():  # noqa: ANN202
            abort(400)

        response = client.get("/test-bad-request")
        assert response.status_code == 400
        data = response.get_json()
        assert data["error"]["code"] == "INVALID_REQUEST"

    def test_429_handler(self, app, client) -> None:
        """Test the 429 rate limit handler."""
        from flask import abort

        @app.route("/test-rate-limit")
        def trigger_rate_limit():  # noqa: ANN202
            abort(429)

        response = client.get("/test-rate-limit")
        assert response.status_code == 429
        data = response.get_json()
        assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"
