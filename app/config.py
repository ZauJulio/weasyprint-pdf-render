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

    # CORS
    CORS_ORIGINS: list[str] = field(
        default_factory=lambda: os.getenv("CORS_ORIGINS", "*").split(",")
    )
    CORS_MAX_AGE: int = field(default_factory=lambda: int(os.getenv("CORS_MAX_AGE", "600")))

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = field(
        default_factory=lambda: os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    )
    RATE_LIMIT_DEFAULT: str = field(
        default_factory=lambda: os.getenv("RATE_LIMIT_DEFAULT", "60/minute")
    )
    RATE_LIMIT_RENDER: str = field(
        default_factory=lambda: os.getenv("RATE_LIMIT_RENDER", "20/minute")
    )

    # Security
    FORCE_HTTPS: bool = field(
        default_factory=lambda: os.getenv("FORCE_HTTPS", "false").lower() == "true"
    )

    # API Key authentication (opt-in: empty string = disabled)
    API_KEY: str = field(default_factory=lambda: os.getenv("API_KEY", ""))
    API_KEY_HEADER: str = field(default_factory=lambda: os.getenv("API_KEY_HEADER", "X-API-Key"))

    @property
    def max_html_size_bytes(self) -> int:
        return self.MAX_HTML_SIZE_MB * 1024 * 1024


def get_config() -> Config:
    """Get application configuration."""
    return Config()
