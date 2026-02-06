"""Tests for API routes."""

from __future__ import annotations

import base64


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_returns_200(self, client) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"
        assert data["service"] == "pdf-render"


class TestRenderEndpoint:
    """Tests for the POST /api/v1/render endpoint."""

    def test_simple_render(self, client, simple_html_b64: str) -> None:
        response = client.post(
            "/api/v1/render",
            json={"html": simple_html_b64},
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.get_json()
        assert "pdf" in data
        assert "metadata" in data
        assert data["metadata"]["pages"] >= 1
        assert data["metadata"]["size_bytes"] > 0
        assert data["metadata"]["rendering_time_ms"] >= 0
        # Verify PDF content
        pdf_bytes = base64.b64decode(data["pdf"])
        assert pdf_bytes[:5] == b"%PDF-"

    def test_render_complex_html(self, client, complex_html_b64: str) -> None:
        response = client.post(
            "/api/v1/render",
            json={"html": complex_html_b64},
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["metadata"]["pages"] >= 1

    def test_render_html_with_base64_image(self, client, html_with_base64_image_b64: str) -> None:
        response = client.post(
            "/api/v1/render",
            json={"html": html_with_base64_image_b64},
            content_type="application/json",
        )
        assert response.status_code == 200

    def test_missing_html_field(self, client) -> None:
        response = client.post(
            "/api/v1/render",
            json={"not_html": "something"},
            content_type="application/json",
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["error"]["code"] == "HTML_REQUIRED"

    def test_empty_html_field(self, client) -> None:
        response = client.post(
            "/api/v1/render",
            json={"html": ""},
            content_type="application/json",
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["error"]["code"] == "HTML_REQUIRED"

    def test_invalid_base64(self, client) -> None:
        response = client.post(
            "/api/v1/render",
            json={"html": "!!!not-base64!!!"},
            content_type="application/json",
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["error"]["code"] == "INVALID_BASE64"

    def test_javascript_rejected(self, client, html_with_script_b64: str) -> None:
        response = client.post(
            "/api/v1/render",
            json={"html": html_with_script_b64},
            content_type="application/json",
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["error"]["code"] == "JAVASCRIPT_DETECTED"

    def test_event_handler_rejected(self, client, html_with_event_handler_b64: str) -> None:
        response = client.post(
            "/api/v1/render",
            json={"html": html_with_event_handler_b64},
            content_type="application/json",
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["error"]["code"] == "JAVASCRIPT_DETECTED"

    def test_wrong_content_type(self, client) -> None:
        response = client.post(
            "/api/v1/render",
            data="not json",
            content_type="text/plain",
        )
        assert response.status_code == 415
        data = response.get_json()
        assert data["error"]["code"] == "UNSUPPORTED_MEDIA_TYPE"

    def test_invalid_json_body(self, client) -> None:
        response = client.post(
            "/api/v1/render",
            data="{bad json",
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_html_too_large(self, client) -> None:
        # Test config limits to 1MB
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

    def test_not_found(self, client) -> None:
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404


class TestSwaggerEndpoint:
    """Tests for the Swagger documentation endpoint."""

    def test_apidocs_accessible(self, client) -> None:
        response = client.get("/apidocs/")
        assert response.status_code == 200

    def test_apispec_json(self, client) -> None:
        response = client.get("/apispec.json")
        assert response.status_code == 200
        data = response.get_json()
        assert "info" in data
        assert data["info"]["title"] == "PDF Render API"
