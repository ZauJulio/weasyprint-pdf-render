"""HTML sanitization and validation service."""

from __future__ import annotations

import base64
import logging
import re

import bleach
from bleach.css_sanitizer import CSSSanitizer

from app.errors import (
    HtmlTooLargeError,
    InvalidBase64Error,
    JavaScriptDetectedError,
    SanitizationError,
)

# CSS sanitizer for inline styles
CSS_SANITIZER = CSSSanitizer(
    allowed_css_properties=[
        "background",
        "background-color",
        "background-image",
        "background-position",
        "background-repeat",
        "background-size",
        "border",
        "border-bottom",
        "border-collapse",
        "border-color",
        "border-left",
        "border-radius",
        "border-right",
        "border-spacing",
        "border-style",
        "border-top",
        "border-width",
        "color",
        "cursor",
        "direction",
        "display",
        "float",
        "font",
        "font-family",
        "font-size",
        "font-style",
        "font-variant",
        "font-weight",
        "height",
        "width",
        "max-height",
        "max-width",
        "min-height",
        "min-width",
        "letter-spacing",
        "line-height",
        "list-style",
        "list-style-type",
        "margin",
        "margin-bottom",
        "margin-left",
        "margin-right",
        "margin-top",
        "opacity",
        "outline",
        "overflow",
        "padding",
        "padding-bottom",
        "padding-left",
        "padding-right",
        "padding-top",
        "page-break-after",
        "page-break-before",
        "page-break-inside",
        "position",
        "left",
        "right",
        "top",
        "bottom",
        "table-layout",
        "text-align",
        "text-decoration",
        "text-indent",
        "text-transform",
        "vertical-align",
        "visibility",
        "white-space",
        "word-spacing",
        "word-wrap",
        "z-index",
    ]
)

logger = logging.getLogger(__name__)

# Allowed HTML tags for sanitization
ALLOWED_TAGS = [
    "html",
    "head",
    "body",
    "title",
    "meta",
    "link",
    "style",
    "div",
    "span",
    "p",
    "br",
    "hr",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "strong",
    "em",
    "b",
    "i",
    "u",
    "s",
    "sub",
    "sup",
    "ul",
    "ol",
    "li",
    "dl",
    "dt",
    "dd",
    "table",
    "thead",
    "tbody",
    "tfoot",
    "tr",
    "th",
    "td",
    "caption",
    "colgroup",
    "col",
    "a",
    "img",
    "blockquote",
    "pre",
    "code",
    "figure",
    "figcaption",
    "header",
    "footer",
    "nav",
    "main",
    "section",
    "article",
    "aside",
    "details",
    "summary",
    "abbr",
    "address",
    "cite",
    "q",
    "small",
    "time",
    "var",
    "svg",
    "path",
    "g",
    "rect",
    "circle",
    "line",
    "polyline",
    "polygon",
    "text",
    "defs",
    "use",
    "clippath",
]

# Allowed attributes per tag
ALLOWED_ATTRIBUTES: dict[str, list[str]] = {
    "*": ["class", "id", "style", "lang", "dir", "title", "data-*", "role", "aria-*"],
    "a": ["href", "target", "rel"],
    "img": ["src", "alt", "width", "height"],
    "meta": ["charset", "name", "content", "http-equiv"],
    "link": ["rel", "href", "type", "media"],
    "td": ["colspan", "rowspan", "headers"],
    "th": ["colspan", "rowspan", "scope", "headers"],
    "col": ["span"],
    "colgroup": ["span"],
    "ol": ["start", "type", "reversed"],
    "time": ["datetime"],
    "svg": ["viewbox", "xmlns", "width", "height", "fill", "stroke"],
    "path": ["d", "fill", "stroke", "stroke-width", "transform"],
    "g": ["transform", "fill", "stroke"],
    "rect": ["x", "y", "width", "height", "rx", "ry", "fill", "stroke"],
    "circle": ["cx", "cy", "r", "fill", "stroke"],
    "line": ["x1", "y1", "x2", "y2", "stroke", "stroke-width"],
    "polyline": ["points", "fill", "stroke"],
    "polygon": ["points", "fill", "stroke"],
    "text": ["x", "y", "font-size", "fill", "text-anchor"],
    "use": ["href", "x", "y", "width", "height"],
    "clippath": ["id"],
}

# Patterns to detect JavaScript
JS_PATTERNS = [
    re.compile(r"<script[\s>]", re.IGNORECASE),
    re.compile(r"</script>", re.IGNORECASE),
    re.compile(r"\bon\w+\s*=", re.IGNORECASE),  # event handlers like onclick=
    re.compile(r"javascript\s*:", re.IGNORECASE),  # javascript: protocol
    re.compile(r"vbscript\s*:", re.IGNORECASE),  # vbscript: protocol
    re.compile(r"data\s*:\s*text/html", re.IGNORECASE),  # data:text/html
    re.compile(r"expression\s*\(", re.IGNORECASE),  # CSS expression()
]


def decode_base64_html(encoded_html: str) -> str:
    """Decode a base64-encoded HTML string.

    Args:
        encoded_html: Base64-encoded HTML string.

    Returns:
        Decoded HTML string.

    Raises:
        InvalidBase64Error: If the string is not valid base64.
    """
    try:
        decoded_bytes = base64.b64decode(encoded_html, validate=True)
        return decoded_bytes.decode("utf-8")
    except Exception as exc:
        logger.warning("Failed to decode base64 HTML: %s", str(exc))
        raise InvalidBase64Error from exc


def decode_base64_to_bytes(encoded_data: str) -> bytes:
    """Decode a base64-encoded string to bytes.

    Args:
        encoded_data: Base64-encoded string.

    Returns:
        Decoded bytes.

    Raises:
        InvalidBase64Error: If the string is not valid base64.
    """
    try:
        return base64.b64decode(encoded_data, validate=True)
    except Exception as exc:
        logger.warning("Failed to decode base64 content: %s", str(exc))
        raise InvalidBase64Error from exc


def check_html_size(html: str, max_size_bytes: int, max_size_mb: int) -> None:
    """Check if HTML content exceeds the maximum allowed size.

    Args:
        html: HTML content string.
        max_size_bytes: Maximum allowed size in bytes.
        max_size_mb: Maximum allowed size in MB (for error message).

    Raises:
        HtmlTooLargeError: If the HTML exceeds the size limit.
    """
    html_size = len(html.encode("utf-8"))
    if html_size > max_size_bytes:
        logger.warning(
            "HTML content too large: %d bytes (max: %d bytes)",
            html_size,
            max_size_bytes,
        )
        raise HtmlTooLargeError(max_size_mb=max_size_mb)


def detect_javascript(html: str) -> list[str]:
    """Detect JavaScript in HTML content.

    Args:
        html: HTML content to check.

    Returns:
        List of detected JS pattern descriptions.
    """
    detections: list[str] = []
    for pattern in JS_PATTERNS:
        matches = pattern.findall(html)
        if matches:
            detections.append(f"Pattern '{pattern.pattern}' found {len(matches)} time(s)")
    return detections


def check_no_javascript(html: str) -> None:
    """Verify that HTML contains no JavaScript.

    Args:
        html: HTML content to check.

    Raises:
        JavaScriptDetectedError: If JavaScript is found.
    """
    detections = detect_javascript(html)
    if detections:
        logger.warning("JavaScript detected in HTML: %s", detections)
        raise JavaScriptDetectedError(details={"detections": detections})


def sanitize_html(html: str) -> str:
    """Sanitize HTML content by removing dangerous elements and attributes.

    Allows only safe tags and attributes. Strips all script tags,
    event handlers, and other potentially dangerous content.

    Args:
        html: Raw HTML content.

    Returns:
        Sanitized HTML content.

    Raises:
        SanitizationError: If sanitization fails unexpectedly.
    """
    try:
        cleaned = bleach.clean(
            html,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            protocols=["http", "https", "mailto", "data"],
            css_sanitizer=CSS_SANITIZER,
            strip=True,
            strip_comments=True,
        )
        logger.debug("HTML sanitized successfully")
        return cleaned
    except Exception as exc:
        logger.error("HTML sanitization failed: %s", str(exc))
        raise SanitizationError(details={"reason": str(exc)}) from exc


def validate_and_sanitize(
    encoded_html: str,
    max_size_bytes: int,
    max_size_mb: int,
) -> str:
    """Full pipeline: decode, size check, JS check, sanitize.

    Args:
        encoded_html: Base64-encoded HTML string.
        max_size_bytes: Maximum allowed HTML size in bytes.
        max_size_mb: Maximum allowed HTML size in MB.

    Returns:
        Sanitized HTML content ready for rendering.
    """
    logger.info("Starting HTML validation and sanitization pipeline")

    html = decode_base64_html(encoded_html)
    check_html_size(html, max_size_bytes, max_size_mb)
    check_no_javascript(html)
    sanitized = sanitize_html(html)

    logger.info("HTML validation and sanitization completed successfully")
    return sanitized
