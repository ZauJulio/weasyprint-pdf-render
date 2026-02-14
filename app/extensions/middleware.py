"""Request middleware for logging, request IDs, and timing."""

from __future__ import annotations

import logging
import time
import uuid

from flask import Flask, g, request

logger = logging.getLogger(__name__)


def init_middleware(app: Flask) -> None:
    """Register before/after request hooks for cross-cutting concerns.

    Adds:
    - Unique request ID (X-Request-ID header)
    - Request timing (X-Response-Time header)
    - Structured request/response logging

    Args:
        app: Flask application instance.
    """

    @app.before_request
    def _before_request() -> None:
        g.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        g.start_time = time.perf_counter()

        logger.info(
            "Request started: %s %s",
            request.method,
            request.path,
            extra={"request_id": g.request_id},
        )

    @app.after_request
    def _after_request(response):  # noqa: ANN001, ANN202
        elapsed_ms = (time.perf_counter() - g.get("start_time", time.perf_counter())) * 1000
        request_id = g.get("request_id", "unknown")

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{elapsed_ms:.2f}ms"

        logger.info(
            "Request completed: %s %s -> %d (%.2fms)",
            request.method,
            request.path,
            response.status_code,
            elapsed_ms,
            extra={"request_id": request_id, "status_code": response.status_code},
        )

        return response
