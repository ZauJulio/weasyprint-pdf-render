"""Test fixtures and shared configuration."""

from __future__ import annotations

import base64

import pytest

from app.config import Config
from app.factory import create_app


@pytest.fixture()
def test_config() -> Config:
    """Create a test configuration."""
    return Config(
        FLASK_ENV="testing",
        DEBUG=True,
        LOG_LEVEL="DEBUG",
        MAX_HTML_SIZE_MB=1,
        OTEL_ENABLED=False,
    )


@pytest.fixture()
def app(test_config: Config):
    """Create a Flask test application."""
    application = create_app(config=test_config)
    application.config["TESTING"] = True
    return application


@pytest.fixture()
def client(app):
    """Create a Flask test client."""
    return app.test_client()


@pytest.fixture()
def simple_html() -> str:
    """Simple valid HTML content."""
    return "<html><body><h1>Hello World</h1></body></html>"


@pytest.fixture()
def simple_html_b64(simple_html: str) -> str:
    """Base64-encoded simple HTML."""
    return base64.b64encode(simple_html.encode()).decode()


@pytest.fixture()
def html_with_script() -> str:
    """HTML content containing JavaScript."""
    return "<html><body><script>alert('xss')</script></body></html>"


@pytest.fixture()
def html_with_script_b64(html_with_script: str) -> str:
    """Base64-encoded HTML with script."""
    return base64.b64encode(html_with_script.encode()).decode()


@pytest.fixture()
def html_with_event_handler() -> str:
    """HTML with inline event handler."""
    return '<html><body><div onclick="alert(1)">Click</div></body></html>'


@pytest.fixture()
def html_with_event_handler_b64(html_with_event_handler: str) -> str:
    """Base64-encoded HTML with event handler."""
    return base64.b64encode(html_with_event_handler.encode()).decode()


@pytest.fixture()
def html_with_base64_image() -> str:
    """HTML with a base64-embedded image."""
    img = (
        "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg"
        "AAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVQI12P4/58B"
        "AAIBAMNJQymQAAAABJRU5ErkJggg=="
    )
    return f'<html><body><img src="{img}" alt="pixel"/></body></html>'


@pytest.fixture()
def html_with_base64_image_b64(html_with_base64_image: str) -> str:
    """Base64-encoded HTML with base64 image."""
    return base64.b64encode(html_with_base64_image.encode()).decode()


@pytest.fixture()
def complex_html() -> str:
    """Complex HTML with styles and structure."""
    return """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; }
            .header { color: #333; font-size: 24px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        </style>
    </head>
    <body>
        <h1 class="header">Report</h1>
        <p>Generated on 2025-01-01</p>
        <table>
            <thead>
                <tr><th>Item</th><th>Value</th></tr>
            </thead>
            <tbody>
                <tr><td>A</td><td>100</td></tr>
                <tr><td>B</td><td>200</td></tr>
            </tbody>
        </table>
    </body>
    </html>
    """


@pytest.fixture()
def complex_html_b64(complex_html: str) -> str:
    """Base64-encoded complex HTML."""
    return base64.b64encode(complex_html.encode()).decode()
