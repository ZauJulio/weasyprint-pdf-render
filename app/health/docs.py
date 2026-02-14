"""Swagger/OpenAPI documentation for the health endpoint."""

from __future__ import annotations

HEALTH_SPEC: dict = {
    "tags": ["Health"],
    "summary": "Health check",
    "description": "Returns the health status of the service.",
    "produces": ["application/json"],
    "security": [],
    "responses": {
        "200": {
            "description": "Service is healthy",
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
            },
        }
    },
}
