"""Tests for rate limiting."""

from __future__ import annotations

from app.config import Config
from app.factory import create_app


class TestRateLimiting:
    """Tests for rate limit enforcement."""

    def test_rate_limit_disabled_in_test_config(self, client) -> None:
        """Rate limiting should be disabled in test fixtures (no 429)."""
        for _ in range(100):
            response = client.get("/health")
            assert response.status_code == 200

    def test_rate_limit_enforced_when_enabled(self) -> None:
        """When enabled with a tight limit, requests should be throttled."""
        config = Config(
            FLASK_ENV="testing",
            DEBUG=True,
            LOG_LEVEL="DEBUG",
            MAX_HTML_SIZE_MB=1,
            OTEL_ENABLED=False,
            RATE_LIMIT_ENABLED=True,
            RATE_LIMIT_DEFAULT="2/minute",
            RATE_LIMIT_RENDER="2/minute",
            FORCE_HTTPS=False,
            CORS_ORIGINS=["*"],
        )
        app = create_app(config=config)
        # NOTE: do NOT set app.config["TESTING"] = True here — flask-limiter
        # skips enforcement when TESTING is True.
        client = app.test_client()

        # First 2 should succeed
        for _ in range(2):
            response = client.get("/health")
            assert response.status_code == 200

        # Third should be rate limited
        response = client.get("/health")
        assert response.status_code == 429
        data = response.get_json()
        assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"

    def test_rate_limit_render_endpoint(self) -> None:
        """The render endpoint should have its own rate limit."""
        config = Config(
            FLASK_ENV="testing",
            DEBUG=True,
            LOG_LEVEL="DEBUG",
            MAX_HTML_SIZE_MB=1,
            OTEL_ENABLED=False,
            RATE_LIMIT_ENABLED=True,
            RATE_LIMIT_DEFAULT="100/minute",
            RATE_LIMIT_RENDER="1/minute",
            FORCE_HTTPS=False,
            CORS_ORIGINS=["*"],
        )
        app = create_app(config=config)
        # NOTE: do NOT set app.config["TESTING"] = True here — flask-limiter
        # skips enforcement when TESTING is True.
        client = app.test_client()

        import base64

        html_b64 = base64.b64encode(b"<html><body>Hi</body></html>").decode()

        # First request succeeds
        response = client.post(
            "/api/v1/render",
            json={"html": html_b64},
            content_type="application/json",
        )
        assert response.status_code == 200

        # Second request is rate limited
        response = client.post(
            "/api/v1/render",
            json={"html": html_b64},
            content_type="application/json",
        )
        assert response.status_code == 429
