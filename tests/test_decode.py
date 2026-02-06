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
        """Should return 400 if pdf field is missing."""
        response = client.post(
            self.endpoint,
            json={},
            content_type="application/json",
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["error"]["code"] == "INVALID_REQUEST"

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
