"""Tests for PDF rendering service."""

from __future__ import annotations

import base64

from app.renderer import RenderResult, render_html_to_pdf


class TestRenderHtmlToPdf:
    """Tests for the render_html_to_pdf function."""

    def test_simple_html_renders(self, simple_html: str) -> None:
        result = render_html_to_pdf(simple_html)
        assert isinstance(result, RenderResult)
        assert result.pages >= 1
        assert result.size_bytes > 0
        assert result.rendering_time_ms >= 0
        # Verify it's valid base64
        pdf_bytes = base64.b64decode(result.pdf_base64)
        assert pdf_bytes[:5] == b"%PDF-"

    def test_complex_html_renders(self, complex_html: str) -> None:
        result = render_html_to_pdf(complex_html)
        assert result.pages >= 1
        pdf_bytes = base64.b64decode(result.pdf_base64)
        assert pdf_bytes[:5] == b"%PDF-"

    def test_html_with_base64_image(self, html_with_base64_image: str) -> None:
        result = render_html_to_pdf(html_with_base64_image)
        assert result.pages >= 1
        pdf_bytes = base64.b64decode(result.pdf_base64)
        assert pdf_bytes[:5] == b"%PDF-"

    def test_empty_html_renders(self) -> None:
        result = render_html_to_pdf("<html><body></body></html>")
        assert result.pages >= 1

    def test_html_with_styles(self) -> None:
        html = """
        <html>
        <head>
            <style>
                body { background: #f0f0f0; font-size: 16px; }
                h1 { color: navy; }
            </style>
        </head>
        <body><h1>Styled</h1></body>
        </html>
        """
        result = render_html_to_pdf(html)
        assert result.pages >= 1

    def test_invalid_html_still_renders(self) -> None:
        # WeasyPrint is forgiving with malformed HTML
        result = render_html_to_pdf("<h1>No closing tags<p>Broken")
        assert result.pages >= 1

    def test_metadata_populated(self, simple_html: str) -> None:
        result = render_html_to_pdf(simple_html)
        assert result.pdf_base64 != ""
        assert isinstance(result.pages, int)
        assert isinstance(result.size_bytes, int)
        assert isinstance(result.rendering_time_ms, float)
