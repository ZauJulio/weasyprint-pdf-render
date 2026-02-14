"""Tests for Pydantic request/response models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.errors import ErrorDetail, ErrorResponse
from app.features.decode.models import PdfDecodeRequest
from app.features.render.models import RenderMetadata, RenderRequest, RenderResponse


class TestRenderRequest:
    """Tests for the RenderRequest model."""

    def test_valid_html(self) -> None:
        req = RenderRequest(html="PGh0bWw+PC9odG1sPg==")
        assert req.html == "PGh0bWw+PC9odG1sPg=="

    def test_missing_html_raises(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            RenderRequest.model_validate({})
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("html",) for e in errors)

    def test_empty_html_raises(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            RenderRequest(html="")
        errors = exc_info.value.errors()
        assert any(e["type"] == "string_too_short" for e in errors)

    def test_html_must_be_string(self) -> None:
        with pytest.raises(ValidationError):
            RenderRequest.model_validate({"html": 12345})

    def test_extra_fields_ignored(self) -> None:
        req = RenderRequest.model_validate({"html": "abc", "extra": "ignored"})
        assert req.html == "abc"


class TestPdfDecodeRequest:
    """Tests for the PdfDecodeRequest model."""

    def test_valid_pdf(self) -> None:
        req = PdfDecodeRequest(pdf="JVBERi0xLjcK")
        assert req.pdf == "JVBERi0xLjcK"

    def test_missing_pdf_raises(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            PdfDecodeRequest.model_validate({})
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("pdf",) for e in errors)

    def test_empty_pdf_raises(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            PdfDecodeRequest(pdf="")
        errors = exc_info.value.errors()
        assert any(e["type"] == "string_too_short" for e in errors)


class TestRenderMetadata:
    """Tests for the RenderMetadata model."""

    def test_valid_metadata(self) -> None:
        meta = RenderMetadata(pages=2, size_bytes=1024, rendering_time_ms=150.5)
        assert meta.pages == 2
        assert meta.size_bytes == 1024
        assert meta.rendering_time_ms == 150.5


class TestRenderResponse:
    """Tests for the RenderResponse model."""

    def test_valid_response(self) -> None:
        resp = RenderResponse(
            pdf="JVBERi0xLjcK",
            metadata=RenderMetadata(pages=1, size_bytes=500, rendering_time_ms=50.0),
        )
        assert resp.pdf == "JVBERi0xLjcK"
        assert resp.metadata.pages == 1


class TestErrorModels:
    """Tests for error response models."""

    def test_error_detail_without_details(self) -> None:
        detail = ErrorDetail(code="INVALID_REQUEST", message="Bad request")
        assert detail.details is None

    def test_error_detail_with_details(self) -> None:
        detail = ErrorDetail(
            code="VALIDATION_ERROR",
            message="Validation failed",
            details={"errors": [{"loc": ["html"], "msg": "required"}]},
        )
        assert detail.details is not None

    def test_error_response(self) -> None:
        resp = ErrorResponse(error=ErrorDetail(code="NOT_FOUND", message="Not found"))
        assert resp.error.code == "NOT_FOUND"
