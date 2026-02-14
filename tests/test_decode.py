"""Tests for PDF decoding endpoint."""

from __future__ import annotations


class TestDecodePdfEndpoint:
    """Test cases for PDF decoding endpoint."""

    endpoint = "/api/v1/decode/pdf"

    def test_decode_valid_pdf(self, client):
        """Should return decoded PDF file."""
        # Simple PDF "header" in base64
        # %PDF-1.7
        pdf_b64 = "JVBERi0xLjcK"
        response = client.post(
            self.endpoint,
            json={"pdf": pdf_b64},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.mimetype == "application/pdf"
        assert response.data == b"%PDF-1.7\n"

    def test_missing_pdf_field(self, client):
        """Should return 422 if pdf field is missing (Pydantic)."""
        response = client.post(
            self.endpoint,
            json={},
            content_type="application/json",
        )
        assert response.status_code == 422
        data = response.get_json()
        assert data["error"]["code"] == "VALIDATION_ERROR"

    def test_invalid_base64_content(self, client):
        """Should return 400 if pdf content is not valid base64."""
        response = client.post(
            self.endpoint,
            json={"pdf": "not-valid-base64"},
            content_type="application/json",
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["error"]["code"] == "INVALID_BASE64"

    def test_wrong_content_type(self, client):
        """Should return 415 if content type is not JSON."""
        response = client.post(
            self.endpoint,
            data="not json",
            content_type="text/plain",
        )
        assert response.status_code == 415
        data = response.get_json()
        assert data["error"]["code"] == "UNSUPPORTED_MEDIA_TYPE"

    def test_invalid_json_body(self, client):
        """Should return 400 if JSON body is malformed."""
        response = client.post(
            self.endpoint,
            data="{bad json",
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_empty_pdf_string(self, client):
        """Should return 422 if pdf field is an empty string (Pydantic min_length)."""
        response = client.post(
            self.endpoint,
            json={"pdf": ""},
            content_type="application/json",
        )
        assert response.status_code == 422
        data = response.get_json()
        assert data["error"]["code"] == "VALIDATION_ERROR"

    def test_pdf_field_not_string(self, client):
        """Should return 422 if pdf field is not a string (Pydantic)."""
        response = client.post(
            self.endpoint,
            json={"pdf": 12345},
            content_type="application/json",
        )
        assert response.status_code == 422
        data = response.get_json()
        assert data["error"]["code"] == "VALIDATION_ERROR"
