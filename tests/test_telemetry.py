"""Tests for OpenTelemetry configuration."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from flask import Flask

from app.extensions.telemetry import init_telemetry


class TestInitTelemetry:
    """Tests for init_telemetry function."""

    def test_disabled_telemetry_is_noop(self) -> None:
        """Telemetry should be a no-op when disabled."""
        mock_app = MagicMock(spec=Flask)
        # Should not raise
        init_telemetry(
            mock_app, enabled=False, service_name="test", endpoint="http://localhost:4317"
        )

    def test_enabled_telemetry_instruments_app(self) -> None:
        """Should initialize OTEL providers and instrument the app when enabled."""
        mock_app = MagicMock(spec=Flask)

        mock_resource = MagicMock()
        mock_provider = MagicMock()
        mock_exporter = MagicMock()
        mock_processor = MagicMock()
        mock_instrumentor_instance = MagicMock()

        with (
            patch(
                "opentelemetry.sdk.resources.Resource.create", return_value=mock_resource
            ) as mock_resource_create,
            patch("opentelemetry.sdk.trace.TracerProvider", return_value=mock_provider),
            patch(
                "opentelemetry.exporter.otlp.proto.grpc.trace_exporter.OTLPSpanExporter",
                return_value=mock_exporter,
            ),
            patch(
                "opentelemetry.sdk.trace.export.BatchSpanProcessor",
                return_value=mock_processor,
            ),
            patch("opentelemetry.trace.set_tracer_provider") as mock_set_tracer,
            patch(
                "opentelemetry.instrumentation.flask.FlaskInstrumentor",
                return_value=mock_instrumentor_instance,
            ),
        ):
            init_telemetry(
                mock_app,
                enabled=True,
                service_name="test-service",
                endpoint="http://localhost:4317",
            )

            mock_resource_create.assert_any_call({"service.name": "test-service"})
            mock_provider.add_span_processor.assert_called_once_with(mock_processor)
            mock_set_tracer.assert_called_once_with(mock_provider)
            mock_instrumentor_instance.instrument_app.assert_called_once_with(mock_app)

    def test_import_error_handled_gracefully(self) -> None:
        """Should log warning and continue when OTEL packages are missing."""
        mock_app = MagicMock(spec=Flask)

        # Simulate ImportError by making the first import fail
        original_import = (
            __builtins__.__import__ if hasattr(__builtins__, "__import__") else __import__
        )

        def mock_import(name, *args, **kwargs):
            if name.startswith("opentelemetry"):
                raise ImportError(f"No module named '{name}'")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            # Should not raise - handles ImportError internally
            init_telemetry(
                mock_app,
                enabled=True,
                service_name="test",
                endpoint="http://localhost:4317",
            )

    def test_generic_exception_handled_gracefully(self) -> None:
        """Should log error and continue on unexpected exceptions."""
        mock_app = MagicMock(spec=Flask)

        with patch(
            "opentelemetry.sdk.resources.Resource.create",
            side_effect=RuntimeError("Unexpected error"),
        ):
            # Should not raise - handles Exception internally
            init_telemetry(
                mock_app,
                enabled=True,
                service_name="test",
                endpoint="http://localhost:4317",
            )
