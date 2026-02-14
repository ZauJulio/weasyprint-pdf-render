"""Swagger/OpenAPI documentation for the decode endpoint."""

from __future__ import annotations

DECODE_SPEC: dict = {
    "tags": ["PDF Rendering"],
    "summary": "Decode base64 PDF to file",
    "description": "Receives a base64-encoded PDF and returns the decoded PDF file.",
    "consumes": ["application/json"],
    "produces": ["application/pdf"],
    "parameters": [
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "$ref": "#/definitions/PdfDecodeRequest",
            },
            "description": "Base64-encoded PDF to decode.",
        }
    ],
    "responses": {
        "200": {
            "description": "PDF file",
            "schema": {
                "type": "file",
            },
        },
        "400": {
            "description": "Bad request",
            "schema": {
                "$ref": "#/definitions/ErrorResponse",
            },
        },
        "401": {
            "description": "Unauthorized — invalid or missing API key",
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
    },
}
