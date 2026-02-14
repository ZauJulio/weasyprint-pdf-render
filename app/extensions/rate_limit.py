"""Rate limiting configuration using Flask-Limiter."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

if TYPE_CHECKING:
    from flask import Flask

logger = logging.getLogger(__name__)

# Module-level limiter instance so blueprints can import decorators.
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",
    strategy="fixed-window",
)


def init_rate_limit(app: Flask, *, default_limit: str, enabled: bool) -> None:
    """Attach the rate limiter to the Flask application.

    Args:
        app: Flask application instance.
        default_limit: Default rate limit string (e.g. ``"60/minute"``).
        enabled: Whether rate limiting is active.
    """
    app.config["RATELIMIT_ENABLED"] = enabled
    app.config["RATELIMIT_DEFAULT"] = default_limit

    # When the module-level singleton is re-used across multiple ``create_app``
    # calls (common in tests), stale state must be cleared so ``init_app``
    # picks up the *new* app's configuration rather than keeping values cached
    # from a previous initialisation.
    limiter.limit_manager._default_limits = []

    limiter.init_app(app)

    # Forcefully synchronise the singleton's enabled flag — ``init_app`` uses
    # ``config.setdefault`` which won't overwrite an existing key.
    limiter.enabled = enabled

    if not enabled:
        logger.info("Rate limiting is disabled")
    else:
        logger.info("Rate limiting enabled: default=%s", default_limit)

    # Clear any counters left over from a previous app initialisation
    # (important when the module-level singleton is reused across tests).
    if enabled and limiter._storage:
        limiter.reset()
