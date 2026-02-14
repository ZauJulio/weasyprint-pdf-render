"""Swagger/OpenAPI documentation for the render endpoint."""

from __future__ import annotations

# Base64 of: <html><body><h1>Hello World</h1></body></html>
_EXAMPLE_B64 = "PGh0bWw+PGJvZHk+PGgxPkhlbGxvIFdvcmxkPC9oMT48L2JvZHk+PC9odG1sPg=="

RENDER_SPEC: dict = {
    "tags": ["PDF Rendering"],
    "summary": "Render HTML to PDF",
    "description": (
        "Receives a base64-encoded HTML string, sanitizes it, "
        "validates it (no JavaScript allowed), and renders it "
        "to a PDF document.\n\n"
        "**Flow:**\n"
        "1. Validate request body via Pydantic model\n"
        "2. Decode the base64 HTML\n"
        "3. Check size limits\n"
        "4. Detect and reject JavaScript\n"
        "5. Sanitize HTML (remove unsafe tags/attributes)\n"
        "6. Render to PDF via WeasyPrint\n"
        "7. Return base64-encoded PDF"
    ),
    "consumes": ["application/json"],
    "produces": ["application/json"],
    "parameters": [
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "$ref": "#/definitions/RenderRequest",
            },
            "description": "HTML content to render as PDF.",
        }
    ],
    "responses": {
        "200": {
            "description": "PDF rendered successfully",
            "schema": {
                "$ref": "#/definitions/RenderResponse",
            },
            "examples": {
                "application/json": {
                    "pdf": "JVBERi0xLjcK...",
                    "metadata": {
                        "pages": 1,
                        "size_bytes": 12345,
                        "rendering_time_ms": 150.5,
                    },
                }
            },
        },
        "400": {
            "description": "Validation error",
            "schema": {
                "$ref": "#/definitions/ErrorResponse",
            },
            "examples": {
                "application/json": {
                    "error": {
                        "code": "INVALID_BASE64",
                        "message": "Invalid base64.",
                    }
                }
            },
        },
        "401": {
            "description": "Unauthorized — invalid or missing API key",
            "schema": {
                "$ref": "#/definitions/ErrorResponse",
            },
        },
        "413": {
            "description": "HTML content too large",
            "schema": {
                "$ref": "#/definitions/ErrorResponse",
            },
        },
        "415": {
            "description": "Unsupported media type",
            "schema": {
                "$ref": "#/definitions/ErrorResponse",
            },
        },
        "422": {
            "description": "Validation error (Pydantic)",
            "schema": {
                "$ref": "#/definitions/ErrorResponse",
            },
        },
        "429": {
            "description": "Rate limit exceeded",
            "schema": {
                "$ref": "#/definitions/ErrorResponse",
            },
        },
        "500": {
            "description": "Internal server error",
            "schema": {
                "$ref": "#/definitions/ErrorResponse",
            },
        },
    },
}
