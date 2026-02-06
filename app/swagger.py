"""Swagger/OpenAPI configuration."""

from __future__ import annotations

SWAGGER_TEMPLATE = {
    "openapi": "3.0.3",
    "swagger": None,  # Explicitly remove swagger field to avoid version conflict
    "info": {
        "title": "PDF Render API",
        "description": (
            "A microservice that receives base64-encoded HTML and renders it to PDF "
            "using WeasyPrint. The HTML is sanitized and validated before rendering. "
            "JavaScript is not allowed."
        ),
        "version": "1.0.0",
        "contact": {"name": "PDF Render Team"},
        "license": {"name": "MIT"},
    },
    "servers": [{"url": "/", "description": "Local development server"}],
    "tags": [
        {
            "name": "PDF Rendering",
            "description": "Endpoints for HTML to PDF conversion",
        },
        {
            "name": "Health",
            "description": "Health check endpoints",
        },
    ],
    "components": {
        "schemas": {
            "RenderRequest": {
                "type": "object",
                "required": ["html"],
                "properties": {
                    "html": {
                        "type": "string",
                        "description": "Base64-encoded HTML.",
                        "example": "PGh0bWw+PGJvZHk+PGgxPkhlbGxvIFdvcmxkPC9oMT48L2JvZHk+PC9odG1sPg==",  # noqa: E501
                    },
                },
            },
            "PdfDecodeRequest": {
                "type": "object",
                "required": ["pdf"],
                "properties": {
                    "pdf": {
                        "type": "string",
                        "description": "Base64-encoded PDF.",
                        "example": "JVBERi0xLjcK...",
                    },
                },
            },
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Error code.",
                                "example": "INVALID_REQUEST",
                            },
                            "message": {
                                "type": "string",
                                "description": "Error message.",
                                "example": "Invalid request parameters.",
                            },
                            "details": {
                                "type": "object",
                                "description": "Additional error details.",
                            },
                        },
                    }
                },
            },
        }
    },
}

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "uiversion": 3,  # Use Swagger UI 3+
    "specs_route": "/apidocs/",
}
