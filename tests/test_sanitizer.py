"""Tests for HTML sanitization and validation."""

from __future__ import annotations

import base64

import pytest

from app.errors import (
    HtmlTooLargeError,
    InvalidBase64Error,
    JavaScriptDetectedError,
)
from app.sanitizer import (
    check_html_size,
    check_no_javascript,
    decode_base64_html,
    detect_javascript,
    sanitize_html,
    validate_and_sanitize,
)


class TestDecodeBase64Html:
    """Tests for base64 decoding."""

    def test_valid_base64(self) -> None:
        html = "<html><body>Hello</body></html>"
        encoded = base64.b64encode(html.encode()).decode()
        result = decode_base64_html(encoded)
        assert result == html

    def test_invalid_base64_raises(self) -> None:
        with pytest.raises(InvalidBase64Error):
            decode_base64_html("not-valid-base64!!!")

    def test_empty_string(self) -> None:
        # Empty string is valid base64 (decodes to empty bytes)
        result = decode_base64_html("")
        assert result == ""

    def test_unicode_content(self) -> None:
        html = "<html><body>Olá Mundo 你好世界</body></html>"
        encoded = base64.b64encode(html.encode()).decode()
        result = decode_base64_html(encoded)
        assert result == html


class TestCheckHtmlSize:
    """Tests for HTML size validation."""

    def test_within_limit(self) -> None:
        html = "<html>small</html>"
        check_html_size(html, max_size_bytes=1024, max_size_mb=1)

    def test_exceeds_limit_raises(self) -> None:
        html = "x" * 2000
        with pytest.raises(HtmlTooLargeError):
            check_html_size(html, max_size_bytes=1024, max_size_mb=1)

    def test_exactly_at_limit(self) -> None:
        html = "x" * 1024
        check_html_size(html, max_size_bytes=1024, max_size_mb=1)

    def test_one_over_limit_raises(self) -> None:
        html = "x" * 1025
        with pytest.raises(HtmlTooLargeError):
            check_html_size(html, max_size_bytes=1024, max_size_mb=1)


class TestDetectJavascript:
    """Tests for JavaScript detection."""

    def test_no_js(self) -> None:
        html = "<html><body><h1>Safe</h1></body></html>"
        assert detect_javascript(html) == []

    def test_script_tag(self) -> None:
        html = "<html><script>alert(1)</script></html>"
        detections = detect_javascript(html)
        assert len(detections) > 0

    def test_onclick_handler(self) -> None:
        html = '<div onclick="alert(1)">Click</div>'
        detections = detect_javascript(html)
        assert len(detections) > 0

    def test_javascript_protocol(self) -> None:
        html = '<a href="javascript:void(0)">Link</a>'
        detections = detect_javascript(html)
        assert len(detections) > 0

    def test_vbscript_protocol(self) -> None:
        html = '<a href="vbscript:msgbox">Link</a>'
        detections = detect_javascript(html)
        assert len(detections) > 0

    def test_css_expression(self) -> None:
        html = '<div style="width:expression(alert(1))">X</div>'
        detections = detect_javascript(html)
        assert len(detections) > 0

    def test_onload_handler(self) -> None:
        html = '<body onload="alert(1)">'
        detections = detect_javascript(html)
        assert len(detections) > 0

    def test_data_text_html(self) -> None:
        html = '<iframe src="data:text/html,<script>alert(1)</script>">'
        detections = detect_javascript(html)
        assert len(detections) > 0


class TestCheckNoJavascript:
    """Tests for JavaScript check that raises on detection."""

    def test_safe_html_passes(self) -> None:
        check_no_javascript("<html><body><p>Safe</p></body></html>")

    def test_script_raises(self) -> None:
        with pytest.raises(JavaScriptDetectedError):
            check_no_javascript("<script>alert(1)</script>")

    def test_event_handler_raises(self) -> None:
        with pytest.raises(JavaScriptDetectedError):
            check_no_javascript('<div onclick="bad()">X</div>')


class TestSanitizeHtml:
    """Tests for HTML sanitization."""

    def test_preserves_safe_tags(self) -> None:
        html = "<h1>Title</h1><p>Paragraph</p>"
        result = sanitize_html(html)
        assert "<h1>" in result
        assert "<p>" in result

    def test_removes_script_tags(self) -> None:
        html = "<p>Hello</p><script>alert(1)</script>"
        result = sanitize_html(html)
        assert "<script>" not in result
        assert "</script>" not in result

    def test_preserves_styles(self) -> None:
        html = "<style>body { color: red; }</style>"
        result = sanitize_html(html)
        assert "<style>" in result

    def test_preserves_images_with_base64(self) -> None:
        html = '<img src="data:image/png;base64,abc123" alt="test"/>'
        result = sanitize_html(html)
        assert "data:image/png;base64" in result

    def test_preserves_table_structure(self) -> None:
        html = "<table><tr><td>Cell</td></tr></table>"
        result = sanitize_html(html)
        assert "<table>" in result
        assert "<tr>" in result
        assert "<td>" in result

    def test_preserves_classes_and_ids(self) -> None:
        html = '<div class="container" id="main">Content</div>'
        result = sanitize_html(html)
        assert 'class="container"' in result
        assert 'id="main"' in result

    def test_preserves_inline_styles(self) -> None:
        html = '<p style="color: red;">Red text</p>'
        result = sanitize_html(html)
        assert "style=" in result
        assert "color" in result


class TestValidateAndSanitize:
    """Tests for the full validation pipeline."""

    def test_valid_html_passes(self) -> None:
        html = "<html><body><h1>Hello</h1></body></html>"
        encoded = base64.b64encode(html.encode()).decode()
        result = validate_and_sanitize(encoded, max_size_bytes=1024 * 1024, max_size_mb=1)
        assert "<h1>" in result

    def test_invalid_base64_fails(self) -> None:
        with pytest.raises(InvalidBase64Error):
            validate_and_sanitize("!!invalid!!", max_size_bytes=1024, max_size_mb=1)

    def test_too_large_fails(self) -> None:
        html = "x" * 2000
        encoded = base64.b64encode(html.encode()).decode()
        with pytest.raises(HtmlTooLargeError):
            validate_and_sanitize(encoded, max_size_bytes=1024, max_size_mb=1)

    def test_javascript_fails(self) -> None:
        html = "<html><script>alert(1)</script></html>"
        encoded = base64.b64encode(html.encode()).decode()
        with pytest.raises(JavaScriptDetectedError):
            validate_and_sanitize(encoded, max_size_bytes=1024 * 1024, max_size_mb=1)
