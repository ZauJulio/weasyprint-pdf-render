"""Flask application factory."""

from __future__ import annotations

import logging

from flasgger import Swagger
from flask import Flask

from app.config import Config, get_config
from app.errors import register_error_handlers
from app.logging_config import setup_logging
from app.routes import api_bp, health_bp
from app.swagger import SWAGGER_CONFIG, SWAGGER_TEMPLATE
from app.telemetry import init_telemetry

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

    # Register error handlers
    register_error_handlers(app)

    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(api_bp)

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
        "Application initialized: env=%s, otel=%s, max_html=%dMB",
        config.FLASK_ENV,
        config.OTEL_ENABLED,
        config.MAX_HTML_SIZE_MB,
    )
    logger.info(
        "Swagger UI available at: http://%s:%d/apidocs",
        config.HOST,
        config.PORT,
    )

    return app
