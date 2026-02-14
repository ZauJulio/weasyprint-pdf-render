"""API key authentication middleware.

Opt-in: when ``API_KEY`` is set (non-empty), every request must include
the key in the configured header (default ``X-API-Key``).  Requests to
public paths (health check, Swagger UI, API spec) are always exempt.
"""

from __future__ import annotations

import hmac
import logging
from typing import TYPE_CHECKING

from flask import jsonify, request

if TYPE_CHECKING:
    from flask import Flask

logger = logging.getLogger(__name__)

# Paths that never require authentication.
_PUBLIC_PREFIXES: tuple[str, ...] = (
    "/health",
    "/apidocs",
    "/apispec",
    "/flasgger_static",
)


def init_auth(app: Flask, *, api_key: str, header: str) -> None:
    """Register API key authentication on the Flask application.

    If *api_key* is empty the middleware is **disabled** — all requests
    pass through without authentication.

    Args:
        app: Flask application instance.
        api_key: Expected API key value. Empty string disables auth.
        header: HTTP header name to read the key from.
    """
    if not api_key:
        logger.info("API key authentication disabled (API_KEY not set)")
        return

    @app.before_request
    def _check_api_key():  # noqa: ANN202
        # Skip public endpoints
        if any(request.path.startswith(prefix) for prefix in _PUBLIC_PREFIXES):
            return None

        provided = request.headers.get(header, "")

        if not provided or not hmac.compare_digest(provided, api_key):
            logger.warning(
                "Unauthorized request: %s %s",
                request.method,
                request.path,
                extra={"reason": "invalid_api_key"},
            )
            return jsonify(
                {
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "Invalid or missing API key.",
                    }
                }
            ), 401

        return None

    logger.info("API key authentication enabled: header=%s", header)
