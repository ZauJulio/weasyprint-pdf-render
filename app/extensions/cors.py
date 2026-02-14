"""CORS (Cross-Origin Resource Sharing) configuration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from flask_cors import CORS

if TYPE_CHECKING:
    from flask import Flask

logger = logging.getLogger(__name__)


def init_cors(app: Flask, *, origins: list[str], max_age: int) -> None:
    """Initialize CORS on the Flask application.

    Args:
        app: Flask application instance.
        origins: List of allowed origins (e.g. ``["*"]`` or ``["https://example.com"]``).
        max_age: Maximum age (in seconds) for preflight request caching.
    """
    CORS(
        app,
        origins=origins,
        methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
        expose_headers=[
            "X-Request-ID",
            "X-Response-Time",
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
        ],
        max_age=max_age,
    )
    logger.info("CORS initialized: origins=%s, max_age=%d", origins, max_age)
