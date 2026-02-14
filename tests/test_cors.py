"""Tests for CORS configuration."""

from __future__ import annotations


class TestCors:
    """Tests for CORS headers on responses."""

    def test_cors_headers_on_get(self, client) -> None:
        """GET requests should include CORS headers."""
        response = client.get("/health", headers={"Origin": "http://example.com"})
        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers

    def test_preflight_options(self, client) -> None:
        """OPTIONS preflight requests should return CORS headers."""
        response = client.options(
            "/api/v1/render",
            headers={
                "Origin": "http://example.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers
        assert "Access-Control-Allow-Methods" in response.headers

    def test_expose_custom_headers(self, client) -> None:
        """Response should expose X-Request-ID and X-Response-Time."""
        response = client.get("/health", headers={"Origin": "http://example.com"})
        exposed = response.headers.get("Access-Control-Expose-Headers", "")
        assert "X-Request-ID" in exposed
        assert "X-Response-Time" in exposed
