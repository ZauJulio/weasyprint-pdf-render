"""Application configuration."""

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Config:
    """Application configuration loaded from environment variables."""

    FLASK_ENV: str = field(default_factory=lambda: os.getenv("FLASK_ENV", "production"))
    DEBUG: bool = field(
        default_factory=lambda: os.getenv("FLASK_ENV", "production") == "development"
    )
    LOG_LEVEL: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    MAX_HTML_SIZE_MB: int = field(default_factory=lambda: int(os.getenv("MAX_HTML_SIZE_MB", "10")))

    # Server
    HOST: str = field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))  # noqa: S104
    PORT: int = field(default_factory=lambda: int(os.getenv("PORT", "5000")))

    # OpenTelemetry
    OTEL_ENABLED: bool = field(
        default_factory=lambda: os.getenv("OTEL_ENABLED", "false").lower() == "true"
    )
    OTEL_SERVICE_NAME: str = field(
        default_factory=lambda: os.getenv("OTEL_SERVICE_NAME", "pdf-render")
    )
    OTEL_EXPORTER_OTLP_ENDPOINT: str = field(
        default_factory=lambda: os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    )

    @property
    def max_html_size_bytes(self) -> int:
        return self.MAX_HTML_SIZE_MB * 1024 * 1024


def get_config() -> Config:
    """Get application configuration."""
    return Config()
