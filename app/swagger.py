"""Global Swagger/OpenAPI configuration.

Uses Swagger 2.0 syntax for full Flasgger compatibility.
"""

from __future__ import annotations

SWAGGER_TEMPLATE: dict = {
    "swagger": "2.0",
    "info": {
        "title": "PDF Render API",
        "description": (
            "A microservice that receives base64-encoded HTML and renders it to PDF "
            "using WeasyPrint. The HTML is sanitized and validated before rendering. "
            "JavaScript is not allowed.\n\n"
            "**Security features:**\n"
            "- API key authentication (opt-in via ``API_KEY`` env var)\n"
            "- Pydantic request validation\n"
            "- Rate limiting (per IP)\n"
            "- CORS protection\n"
            "- Security headers (CSP, HSTS, X-Frame-Options, etc.)\n"
            "- Request ID tracking"
        ),
        "version": "1.1.0",
        "contact": {"name": "PDF Render Team"},
        "license": {"name": "MIT"},
    },
    "basePath": "/",
    "schemes": ["http", "https"],
    "consumes": ["application/json"],
    "produces": ["application/json"],
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
    "securityDefinitions": {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": (
                "API key authentication (opt-in). "
                "Set the API_KEY environment variable to enable. "
                "Health and Swagger endpoints are always public."
            ),
        },
    },
    "security": [
        {"ApiKeyAuth": []},
    ],
    "definitions": {
        "RenderRequest": {
            "type": "object",
            "required": ["html"],
            "properties": {
                "html": {
                    "type": "string",
                    "minLength": 1,
                    "description": "Base64-encoded HTML string.",
                    "example": "PGh0bWw+PGJvZHk+PGgxPkhlbGxvIFdvcmxkPC9oMT48L2JvZHk+PC9odG1sPg==",
                },
            },
        },
        "PdfDecodeRequest": {
            "type": "object",
            "required": ["pdf"],
            "properties": {
                "pdf": {
                    "type": "string",
                    "minLength": 1,
                    "description": "Base64-encoded PDF string.",
                    "example": "JVBERi0xLjcK...",
                },
            },
        },
        "RenderResponse": {
            "type": "object",
            "properties": {
                "pdf": {
                    "type": "string",
                    "description": "Base64-encoded PDF.",
                    "example": "JVBERi0xLjcK...",
                },
                "metadata": {
                    "type": "object",
                    "properties": {
                        "pages": {
                            "type": "integer",
                            "description": "Number of pages.",
                            "example": 1,
                        },
                        "size_bytes": {
                            "type": "integer",
                            "description": "PDF size in bytes.",
                            "example": 12345,
                        },
                        "rendering_time_ms": {
                            "type": "number",
                            "description": "Rendering time in milliseconds.",
                            "example": 150.5,
                        },
                    },
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
                            "description": "Machine-readable error code.",
                            "example": "INVALID_REQUEST",
                        },
                        "message": {
                            "type": "string",
                            "description": "Human-readable error message.",
                            "example": "Invalid request parameters.",
                        },
                        "details": {
                            "type": "object",
                            "description": "Additional error details.",
                        },
                    },
                },
            },
        },
    },
}

SWAGGER_CONFIG: dict = {
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
    "uiversion": 3,
    "specs_route": "/apidocs/",
}
