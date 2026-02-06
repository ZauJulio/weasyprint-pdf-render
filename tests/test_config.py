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
