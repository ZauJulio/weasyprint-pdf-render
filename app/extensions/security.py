"""Security headers configuration (``helmet`` equivalent for Flask).

Uses ``flask-talisman`` to set HTTP security headers such as:
- Content-Security-Policy
- Strict-Transport-Security
- X-Content-Type-Options
- X-Frame-Options
- Referrer-Policy
- Permissions-Policy
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from flask_talisman import Talisman

if TYPE_CHECKING:
    from flask import Flask

logger = logging.getLogger(__name__)


def init_security(app: Flask, *, force_https: bool) -> None:
    """Initialize security headers on the Flask application.

    Args:
        app: Flask application instance.
        force_https: Whether to force HTTPS redirects. Should be ``False``
            during local development.
    """
    csp = {
        "default-src": "'self'",
        "script-src": [
            "'self'",
            "'unsafe-inline'",  # required by Swagger UI
            "'unsafe-eval'",  # required by Swagger UI
            "https://cdn.jsdelivr.net",
        ],
        "style-src": [
            "'self'",
            "'unsafe-inline'",  # required by Swagger UI
            "https://cdn.jsdelivr.net",
        ],
        "img-src": ["'self'", "data:", "https:"],
        "font-src": ["'self'", "https://cdn.jsdelivr.net"],
        "connect-src": "'self'",
    }

    Talisman(
        app,
        force_https=force_https,
        strict_transport_security=True,
        strict_transport_security_max_age=31536000,
        strict_transport_security_include_subdomains=True,
        content_security_policy=csp,
        content_security_policy_nonce_in=[],
        referrer_policy="strict-origin-when-cross-origin",
        permissions_policy={
            "camera": "()",
            "microphone": "()",
            "geolocation": "()",
        },
        session_cookie_secure=force_https,
        session_cookie_http_only=True,
    )

    logger.info("Security headers initialized: force_https=%s", force_https)
