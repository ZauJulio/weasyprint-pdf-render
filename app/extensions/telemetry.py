"""OpenTelemetry configuration and instrumentation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Flask

logger = logging.getLogger(__name__)


def init_telemetry(app: Flask, *, enabled: bool, service_name: str, endpoint: str) -> None:
    """Initialize OpenTelemetry instrumentation for the Flask app.

    Args:
        app: Flask application instance.
        enabled: Whether telemetry is enabled.
        service_name: The OTEL service name.
        endpoint: The OTLP exporter endpoint.
    """
    if not enabled:
        logger.info("OpenTelemetry is disabled")
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.flask import FlaskInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)

        otlp_exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
        processor = BatchSpanProcessor(otlp_exporter)
        provider.add_span_processor(processor)

        trace.set_tracer_provider(provider)

        FlaskInstrumentor().instrument_app(app)

        logger.info(
            "OpenTelemetry initialized: service=%s, endpoint=%s",
            service_name,
            endpoint,
        )
    except ImportError:
        logger.warning("OpenTelemetry packages not installed. Tracing will be disabled.")
    except Exception:
        logger.exception("Failed to initialize OpenTelemetry")
