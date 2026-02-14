"""Tests for security headers (helmet/talisman)."""

from __future__ import annotations


class TestSecurityHeaders:
    """Tests for HTTP security headers set by flask-talisman."""

    def test_content_security_policy(self, client) -> None:
        """Response should include a Content-Security-Policy header."""
        response = client.get("/health")
        assert "Content-Security-Policy" in response.headers
        csp = response.headers["Content-Security-Policy"]
        assert "default-src" in csp

    def test_x_content_type_options(self, client) -> None:
        """Response should include X-Content-Type-Options: nosniff."""
        response = client.get("/health")
        assert response.headers.get("X-Content-Type-Options") == "nosniff"

    def test_x_frame_options(self, client) -> None:
        """Response should include X-Frame-Options."""
        response = client.get("/health")
        # Talisman default is SAMEORIGIN
        assert "X-Frame-Options" in response.headers

    def test_referrer_policy(self, client) -> None:
        """Response should include Referrer-Policy."""
        response = client.get("/health")
        assert "Referrer-Policy" in response.headers
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

    def test_no_force_https_in_test(self, client) -> None:
        """In test config, force_https is False so no HTTPS redirect."""
        response = client.get("/health")
        # Should get 200, not 301/302 redirect
        assert response.status_code == 200

    def test_permissions_policy(self, client) -> None:
        """Response should include Permissions-Policy header."""
        response = client.get("/health")
        pp = response.headers.get("Permissions-Policy", "")
        assert "camera=()" in pp
        assert "microphone=()" in pp
