"""Tests for application configuration."""

from __future__ import annotations

from app.config import Config, get_config


class TestConfig:
    """Tests for Config dataclass."""

    def test_defaults(self) -> None:
        config = Config()
        assert config.FLASK_ENV == "production"
        assert config.LOG_LEVEL == "INFO"
        assert config.MAX_HTML_SIZE_MB == 10
        assert config.OTEL_ENABLED is False

    def test_max_html_size_bytes(self) -> None:
        config = Config(MAX_HTML_SIZE_MB=5)
        assert config.max_html_size_bytes == 5 * 1024 * 1024

    def test_custom_values(self) -> None:
        config = Config(
            FLASK_ENV="testing",
            LOG_LEVEL="DEBUG",
            OTEL_ENABLED=True,
        )
        assert config.FLASK_ENV == "testing"
        assert config.LOG_LEVEL == "DEBUG"
        assert config.OTEL_ENABLED is True

    def test_get_config_returns_config(self) -> None:
        config = get_config()
        assert isinstance(config, Config)

    def test_cors_defaults(self) -> None:
        config = Config()
        assert isinstance(config.CORS_ORIGINS, list)
        assert config.CORS_MAX_AGE == 600

    def test_rate_limit_defaults(self) -> None:
        config = Config()
        assert config.RATE_LIMIT_ENABLED is True
        assert config.RATE_LIMIT_DEFAULT == "60/minute"
        assert config.RATE_LIMIT_RENDER == "20/minute"

    def test_security_defaults(self) -> None:
        config = Config()
        assert config.FORCE_HTTPS is False

    def test_custom_cors_origins(self) -> None:
        config = Config(CORS_ORIGINS=["https://example.com", "https://other.com"])
        assert len(config.CORS_ORIGINS) == 2

    def test_custom_rate_limits(self) -> None:
        config = Config(
            RATE_LIMIT_ENABLED=False,
            RATE_LIMIT_DEFAULT="100/minute",
            RATE_LIMIT_RENDER="50/minute",
        )
        assert config.RATE_LIMIT_ENABLED is False
        assert config.RATE_LIMIT_DEFAULT == "100/minute"
        assert config.RATE_LIMIT_RENDER == "50/minute"
