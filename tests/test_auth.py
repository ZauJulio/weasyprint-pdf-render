"""Tests for API key authentication middleware."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from app.config import Config
from app.factory import create_app

if TYPE_CHECKING:
    from flask import Flask
    from flask.testing import FlaskClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_config(*, api_key: str = "", api_key_header: str = "X-API-Key") -> Config:
    """Create a test config with API key settings."""
    return Config(
        FLASK_ENV="testing",
        DEBUG=True,
        LOG_LEVEL="DEBUG",
        MAX_HTML_SIZE_MB=1,
        OTEL_ENABLED=False,
        RATE_LIMIT_ENABLED=False,
        FORCE_HTTPS=False,
        CORS_ORIGINS=["*"],
        API_KEY=api_key,
        API_KEY_HEADER=api_key_header,
    )


@pytest.fixture()
def app_with_api_key() -> Flask:
    """Create app with API key authentication enabled."""
    app = create_app(config=_make_config(api_key="test-secret-key"))
    app.config["TESTING"] = True
    return app


@pytest.fixture()
def client_with_api_key(app_with_api_key: Flask) -> FlaskClient:
    """Test client for app with API key enabled."""
    return app_with_api_key.test_client()


@pytest.fixture()
def app_custom_header() -> Flask:
    """Create app with a custom API key header name."""
    app = create_app(
        config=_make_config(
            api_key="test-secret-key",
            api_key_header="Authorization",
        )
    )
    app.config["TESTING"] = True
    return app


@pytest.fixture()
def client_custom_header(app_custom_header: Flask) -> FlaskClient:
    """Test client for app with custom API key header."""
    return app_custom_header.test_client()


# ---------------------------------------------------------------------------
# Tests — API key DISABLED (default behavior)
# ---------------------------------------------------------------------------


class TestApiKeyDisabled:
    """When API_KEY is empty, all requests pass through without auth."""

    def test_health_no_key_required(self, client) -> None:
        """Health endpoint works without API key."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_render_no_key_required(self, client) -> None:
        """Protected endpoint works without API key when auth is disabled."""
        response = client.post(
            "/api/v1/render",
            json={"html": "invalid"},
            content_type="application/json",
        )
        # Should get a 400 (bad base64), NOT a 401
        assert response.status_code != 401

    def test_decode_no_key_required(self, client) -> None:
        """Decode endpoint works without API key when auth is disabled."""
        response = client.post(
            "/api/v1/decode/pdf",
            json={"pdf": "invalid"},
            content_type="application/json",
        )
        assert response.status_code != 401


# ---------------------------------------------------------------------------
# Tests — API key ENABLED
# ---------------------------------------------------------------------------


class TestApiKeyEnabled:
    """When API_KEY is set, protected endpoints require the key."""

    # -- Valid key --------------------------------------------------------

    def test_valid_key_passes(self, client_with_api_key) -> None:
        """Request with correct API key is allowed through."""
        response = client_with_api_key.post(
            "/api/v1/render",
            json={"html": "invalid"},
            content_type="application/json",
            headers={"X-API-Key": "test-secret-key"},
        )
        # Should get past auth (400 from bad base64, not 401)
        assert response.status_code != 401

    def test_valid_key_decode(self, client_with_api_key) -> None:
        """Decode endpoint with correct API key passes auth."""
        response = client_with_api_key.post(
            "/api/v1/decode/pdf",
            json={"pdf": "invalid"},
            content_type="application/json",
            headers={"X-API-Key": "test-secret-key"},
        )
        assert response.status_code != 401

    # -- Missing key ------------------------------------------------------

    def test_missing_key_returns_401(self, client_with_api_key) -> None:
        """Request without API key returns 401."""
        response = client_with_api_key.post(
            "/api/v1/render",
            json={"html": "test"},
            content_type="application/json",
        )
        assert response.status_code == 401

    def test_missing_key_error_body(self, client_with_api_key) -> None:
        """401 response has standard error body."""
        response = client_with_api_key.post(
            "/api/v1/render",
            json={"html": "test"},
            content_type="application/json",
        )
        data = response.get_json()
        assert data["error"]["code"] == "UNAUTHORIZED"
        assert "API key" in data["error"]["message"]

    def test_missing_key_decode(self, client_with_api_key) -> None:
        """Decode endpoint without API key returns 401."""
        response = client_with_api_key.post(
            "/api/v1/decode/pdf",
            json={"pdf": "test"},
            content_type="application/json",
        )
        assert response.status_code == 401

    # -- Invalid key ------------------------------------------------------

    def test_wrong_key_returns_401(self, client_with_api_key) -> None:
        """Request with wrong API key returns 401."""
        response = client_with_api_key.post(
            "/api/v1/render",
            json={"html": "test"},
            content_type="application/json",
            headers={"X-API-Key": "wrong-key"},
        )
        assert response.status_code == 401

    def test_empty_key_returns_401(self, client_with_api_key) -> None:
        """Request with empty API key header returns 401."""
        response = client_with_api_key.post(
            "/api/v1/render",
            json={"html": "test"},
            content_type="application/json",
            headers={"X-API-Key": ""},
        )
        assert response.status_code == 401

    # -- Public endpoints are exempt --------------------------------------

    def test_health_exempt(self, client_with_api_key) -> None:
        """Health endpoint is always public, even with API key enabled."""
        response = client_with_api_key.get("/health")
        assert response.status_code == 200

    def test_apidocs_exempt(self, client_with_api_key) -> None:
        """Swagger UI is always public."""
        response = client_with_api_key.get("/apidocs/")
        assert response.status_code == 200

    def test_apispec_exempt(self, client_with_api_key) -> None:
        """API spec JSON is always public."""
        response = client_with_api_key.get("/apispec.json")
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Tests — Custom header name
# ---------------------------------------------------------------------------


class TestApiKeyCustomHeader:
    """API key can be read from a custom header."""

    def test_custom_header_accepted(self, client_custom_header) -> None:
        """Request with key in custom header passes auth."""
        response = client_custom_header.post(
            "/api/v1/render",
            json={"html": "invalid"},
            content_type="application/json",
            headers={"Authorization": "test-secret-key"},
        )
        assert response.status_code != 401

    def test_default_header_rejected(self, client_custom_header) -> None:
        """When custom header is configured, default X-API-Key is ignored."""
        response = client_custom_header.post(
            "/api/v1/render",
            json={"html": "test"},
            content_type="application/json",
            headers={"X-API-Key": "test-secret-key"},
        )
        assert response.status_code == 401

    def test_missing_custom_header_returns_401(self, client_custom_header) -> None:
        """Request without custom header returns 401."""
        response = client_custom_header.post(
            "/api/v1/render",
            json={"html": "test"},
            content_type="application/json",
        )
        assert response.status_code == 401
