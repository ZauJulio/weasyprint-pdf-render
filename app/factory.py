"""Flask application factory."""

from __future__ import annotations

import logging

from flasgger import Swagger
from flask import Flask

from app.config import Config, get_config
from app.errors import register_error_handlers
from app.extensions.auth import init_auth
from app.extensions.cors import init_cors
from app.extensions.logging_config import setup_logging
from app.extensions.middleware import init_middleware
from app.extensions.rate_limit import init_rate_limit
from app.extensions.security import init_security
from app.extensions.telemetry import init_telemetry
from app.features.decode.routes import decode_bp
from app.features.render.routes import render_bp
from app.health.routes import health_bp
from app.swagger import SWAGGER_CONFIG, SWAGGER_TEMPLATE

logger = logging.getLogger(__name__)


def create_app(config: Config | None = None) -> Flask:
    """Create and configure the Flask application.

    Args:
        config: Optional configuration object. Defaults to loading from env.

    Returns:
        Configured Flask application.
    """
    if config is None:
        config = get_config()

    # Setup structured logging first
    setup_logging(level=config.LOG_LEVEL)

    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = config.max_html_size_bytes
    app.config["RATE_LIMIT_RENDER"] = config.RATE_LIMIT_RENDER

    # Register error handlers
    register_error_handlers(app)

    # Initialize middleware (request ID, timing)
    init_middleware(app)

    # Initialize CORS
    init_cors(app, origins=config.CORS_ORIGINS, max_age=config.CORS_MAX_AGE)

    # Initialize rate limiting
    init_rate_limit(
        app,
        default_limit=config.RATE_LIMIT_DEFAULT,
        enabled=config.RATE_LIMIT_ENABLED,
    )

    # Initialize security headers (helmet)
    init_security(app, force_https=config.FORCE_HTTPS)

    # Initialize API key authentication (opt-in)
    init_auth(app, api_key=config.API_KEY, header=config.API_KEY_HEADER)

    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(render_bp)
    app.register_blueprint(decode_bp)

    # Initialize Swagger
    Swagger(app, template=SWAGGER_TEMPLATE, config=SWAGGER_CONFIG)

    # Initialize OpenTelemetry
    init_telemetry(
        app,
        enabled=config.OTEL_ENABLED,
        service_name=config.OTEL_SERVICE_NAME,
        endpoint=config.OTEL_EXPORTER_OTLP_ENDPOINT,
    )

    logger.info(
        "Application initialized: env=%s, otel=%s, max_html=%dMB, "
        "cors=%s, rate_limit=%s, force_https=%s, api_key=%s",
        config.FLASK_ENV,
        config.OTEL_ENABLED,
        config.MAX_HTML_SIZE_MB,
        config.CORS_ORIGINS,
        config.RATE_LIMIT_ENABLED,
        config.FORCE_HTTPS,
        "enabled" if config.API_KEY else "disabled",
    )
    logger.info(
        "Swagger UI available at: http://%s:%d/apidocs",
        config.HOST,
        config.PORT,
    )

    return app
