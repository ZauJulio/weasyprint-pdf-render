"""API route definitions."""

from __future__ import annotations

import io
import logging

from flasgger import swag_from
from flask import Blueprint, jsonify, request, send_file

from app.config import get_config
from app.errors import (
    HtmlRequiredError,
    InvalidRequestError,
    UnsupportedMediaTypeError,
)
from app.renderer import render_html_to_pdf
from app.sanitizer import decode_base64_to_bytes, validate_and_sanitize

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")
health_bp = Blueprint("health", __name__)

# Base64 of: <html><body><h1>Hello World</h1></body></html>
_EXAMPLE_B64 = "PGh0bWw+PGJvZHk+PGgxPkhlbGxvIFdvcmxkPC9oMT48L2JvZHk+PC9odG1sPg=="


@health_bp.route("/health", methods=["GET"])
@swag_from(
    {
        "tags": ["Health"],
        "summary": "Health check",
        "description": "Returns the health status of the service.",
        "responses": {
            "200": {
                "description": "Service is healthy",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "status": {
                                    "type": "string",
                                    "example": "healthy",
                                },
                                "service": {
                                    "type": "string",
                                    "example": "pdf-render",
                                },
                            },
                        }
                    }
                },
            }
        },
    }
)
def health_check():  # noqa: ANN202
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "pdf-render"})


@api_bp.route("/render", methods=["POST"])
@swag_from(
    {
        "tags": ["PDF Rendering"],
        "summary": "Render HTML to PDF",
        "description": (
            "Receives a base64-encoded HTML string, sanitizes it, "
            "validates it (no JavaScript allowed), and renders it "
            "to a PDF document.\n\n"
            "**Flow:**\n"
            "1. Decode the base64 HTML\n"
            "2. Check size limits\n"
            "3. Detect and reject JavaScript\n"
            "4. Sanitize HTML (remove unsafe tags/attributes)\n"
            "5. Render to PDF via WeasyPrint\n"
            "6. Return base64-encoded PDF"
        ),
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/RenderRequest",
                    },
                    "examples": {
                        "simple_html": {
                            "summary": "Simple HTML page",
                            "value": {"html": _EXAMPLE_B64},
                        },
                        "with_base64_image": {
                            "summary": "HTML with base64 image",
                            "value": {
                                "html": (
                                    "PGh0bWw+PGJvZHk+PGgxPlRlc3Q8"
                                    "L2gxPjxpbWcgc3JjPSJkYXRhOmlt"
                                    "YWdlL3BuZztiYXNlNjQsaVZCT1J3"
                                    "MEtHZ29BQUFBTlNVaEVVZ0FBQURF"
                                    "QUFBQUJDQVlBQUFBZkZjU0pBQUFB"
                                    "QzBsRVFWUUkxMlA0Lzc4REFBQUJC"
                                    "Z0FCRFF5bVF3QUFBQUJKU1VSQlZB"
                                    "aVhnd1kiIGFsdD0idGVzdCIvPjwv"
                                    "Ym9keT48L2h0bWw+"
                                ),
                            },
                        },
                    },
                }
            },
        },
        "responses": {
            "200": {
                "description": "PDF rendered successfully",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "pdf": {
                                    "type": "string",
                                    "description": "Base64 PDF.",
                                    "example": "JVBERi0xLjcK...",
                                },
                                "metadata": {
                                    "type": "object",
                                    "properties": {
                                        "pages": {
                                            "type": "integer",
                                            "description": "Pages.",
                                            "example": 1,
                                        },
                                        "size_bytes": {
                                            "type": "integer",
                                            "description": "Size.",
                                            "example": 12345,
                                        },
                                        "rendering_time_ms": {
                                            "type": "number",
                                            "description": "Time (ms).",
                                            "example": 150.5,
                                        },
                                    },
                                },
                            },
                        },
                    }
                },
            },
            "400": {
                "description": "Validation error",
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/ErrorResponse",
                        },
                        "examples": {
                            "html_required": {
                                "summary": "Missing HTML field",
                                "value": {
                                    "error": {
                                        "code": "HTML_REQUIRED",
                                        "message": "Required.",
                                    }
                                },
                            },
                            "invalid_base64": {
                                "summary": "Invalid base64",
                                "value": {
                                    "error": {
                                        "code": "INVALID_BASE64",
                                        "message": "Invalid base64.",
                                    }
                                },
                            },
                            "javascript_detected": {
                                "summary": "JavaScript detected",
                                "value": {
                                    "error": {
                                        "code": "JAVASCRIPT_DETECTED",
                                        "message": "JS not allowed.",
                                        "details": {"detections": ["Pattern found"]},
                                    }
                                },
                            },
                        },
                    }
                },
            },
            "413": {
                "description": "HTML content too large",
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/ErrorResponse",
                        },
                        "examples": {
                            "too_large": {
                                "summary": "Content too large",
                                "value": {
                                    "error": {
                                        "code": "HTML_TOO_LARGE",
                                        "message": "Too large.",
                                        "details": {"max_size_mb": 10},
                                    }
                                },
                            }
                        },
                    }
                },
            },
            "415": {
                "description": "Unsupported media type",
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/ErrorResponse",
                        },
                        "examples": {
                            "wrong_content_type": {
                                "summary": "Wrong Content-Type",
                                "value": {
                                    "error": {
                                        "code": "UNSUPPORTED_MEDIA_TYPE",
                                        "message": "Use JSON.",
                                    }
                                },
                            }
                        },
                    }
                },
            },
            "500": {
                "description": "Internal server error",
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/ErrorResponse",
                        },
                        "examples": {
                            "render_failed": {
                                "summary": "Render failed",
                                "value": {
                                    "error": {
                                        "code": "RENDER_FAILED",
                                        "message": "Render failed.",
                                        "details": {"reason": "Error"},
                                    }
                                },
                            }
                        },
                    }
                },
            },
        },
    }
)
def render_pdf():  # noqa: ANN202
    """Render base64-encoded HTML to PDF."""
    config = get_config()

    # Validate content type
    if not request.is_json:
        raise UnsupportedMediaTypeError

    # Parse request body
    body = request.get_json(silent=True)
    if body is None:
        raise InvalidRequestError(details={"reason": "Request body must be valid JSON."})

    # Validate required field
    encoded_html = body.get("html")
    if not encoded_html or not isinstance(encoded_html, str):
        raise HtmlRequiredError

    # Validate, sanitize, and render
    sanitized_html = validate_and_sanitize(
        encoded_html=encoded_html,
        max_size_bytes=config.max_html_size_bytes,
        max_size_mb=config.MAX_HTML_SIZE_MB,
    )

    result = render_html_to_pdf(sanitized_html)

    logger.info(
        "Request completed: %d pages, %d bytes, %.2fms",
        result.pages,
        result.size_bytes,
        result.rendering_time_ms,
    )

    return jsonify(
        {
            "pdf": result.pdf_base64,
            "metadata": {
                "pages": result.pages,
                "size_bytes": result.size_bytes,
                "rendering_time_ms": result.rendering_time_ms,
            },
        }
    )


@api_bp.route("/decode/pdf", methods=["POST"])
@swag_from(
    {
        "tags": ["PDF Rendering"],
        "summary": "Decode base64 PDF to file",
        "description": "Receives a base64-encoded PDF and returns the decoded PDF file.",
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/PdfDecodeRequest",
                    }
                }
            },
        },
        "responses": {
            "200": {
                "description": "PDF file",
                "content": {
                    "application/pdf": {
                        "schema": {
                            "type": "string",
                            "format": "binary",
                        }
                    }
                },
            },
            "400": {
                "description": "Bad request",
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/ErrorResponse",
                        }
                    }
                },
            },
        },
    }
)
def decode_pdf():  # noqa: ANN202
    """Decode base64 PDF to file."""
    # Validate content type
    if not request.is_json:
        raise UnsupportedMediaTypeError

    # Parse request body
    data = request.get_json(silent=True)
    if data is None:
        raise InvalidRequestError

    if "pdf" not in data:
        raise InvalidRequestError(message="Field 'pdf' is required.")

    pdf_b64 = data.get("pdf")
    if not pdf_b64 or not isinstance(pdf_b64, str):
        raise InvalidRequestError(message="Field 'pdf' must be a non-empty string.")

    # Decode
    pdf_bytes = decode_base64_to_bytes(pdf_b64)

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="decoded.pdf",
    )
