"""Tests for request middleware (request ID, timing)."""

from __future__ import annotations


class TestMiddleware:
    """Tests for before/after request middleware hooks."""

    def test_response_has_request_id(self, client) -> None:
        """Every response should include an X-Request-ID header."""
        response = client.get("/health")
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) > 0

    def test_custom_request_id_is_echoed(self, client) -> None:
        """If the client sends X-Request-ID, it should be echoed back."""
        custom_id = "my-custom-request-id-123"
        response = client.get("/health", headers={"X-Request-ID": custom_id})
        assert response.headers["X-Request-ID"] == custom_id

    def test_response_has_timing_header(self, client) -> None:
        """Every response should include X-Response-Time."""
        response = client.get("/health")
        assert "X-Response-Time" in response.headers
        assert response.headers["X-Response-Time"].endswith("ms")

    def test_generated_request_id_is_uuid(self, client) -> None:
        """Auto-generated request ID should be a valid UUID."""
        import uuid

        response = client.get("/health")
        request_id = response.headers["X-Request-ID"]
        # Should not raise
        uuid.UUID(request_id)
