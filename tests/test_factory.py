"""Tests for Flask application factory."""

from __future__ import annotations

from flask import Flask

from app.factory import create_app


class TestCreateApp:
    """Tests for the create_app factory function."""

    def test_create_app_with_config(self, test_config) -> None:
        """Should create app with provided config."""
        app = create_app(config=test_config)
        assert isinstance(app, Flask)
        assert app.config["TESTING"] is not True  # Not set by factory, only by fixture

    def test_create_app_without_config(self) -> None:
        """Should create app using default config when none is provided."""
        app = create_app()
        assert isinstance(app, Flask)

    def test_app_has_health_blueprint(self, app) -> None:
        """Should register health blueprint."""
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        assert "/health" in rules

    def test_app_has_api_blueprint(self, app) -> None:
        """Should register api blueprint."""
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        assert "/api/v1/render" in rules
        assert "/api/v1/decode/pdf" in rules

    def test_app_has_swagger(self, app) -> None:
        """Should have swagger configured."""
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        assert "/apispec.json" in rules

    def test_app_has_middleware_hooks(self, client) -> None:
        """Should have middleware that adds X-Request-ID."""
        response = client.get("/health")
        assert "X-Request-ID" in response.headers
        assert "X-Response-Time" in response.headers

    def test_app_has_security_headers(self, client) -> None:
        """Should have security headers from flask-talisman."""
        response = client.get("/health")
        assert "Content-Security-Policy" in response.headers
        assert "X-Content-Type-Options" in response.headers

    def test_app_has_cors_headers(self, client) -> None:
        """Should have CORS headers."""
        response = client.get("/health", headers={"Origin": "http://example.com"})
        assert "Access-Control-Allow-Origin" in response.headers
