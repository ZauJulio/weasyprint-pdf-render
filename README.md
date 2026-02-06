<div align="center">

# 📄 PDF Render Microservice

**A high-performance HTML-to-PDF rendering microservice**

[![CI](https://github.com/ZauJulio/weasyprint-pdf-render/actions/workflows/ci.yml/badge.svg)](https://github.com/ZauJulio/weasyprint-pdf-render/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/ZauJulio/weasyprint-pdf-render/branch/main/graph/badge.svg)](https://codecov.io/gh/ZauJulio/weasyprint-pdf-render)
[![Python 3.14+](https://img.shields.io/badge/python-3.14%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![WeasyPrint](https://img.shields.io/badge/WeasyPrint-68-blue)](https://doc.courtbouillon.org/weasyprint/stable/api_reference.html)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GHCR](https://img.shields.io/badge/ghcr.io-zaujulio%2Fpdf--render-2496ED?logo=docker&logoColor=white)](https://ghcr.io/zaujulio/pdf-render)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-261230?logo=ruff&logoColor=white)](https://github.com/astral-sh/ruff)

<br />

Send base64-encoded HTML in, get base64-encoded PDF out. Simple, secure, and fast.

---

</div>

## ✨ Features

| Feature | Description |
| :--- | :--- |
| 🔄 **Base64 I/O** | Receive HTML and return PDF as base64-encoded strings |
| 🛡️ **HTML Sanitization** | Strips scripts, event handlers, and unsafe tags via [bleach](https://github.com/mozilla/bleach) |
| 🚫 **JS Detection** | Rejects HTML containing JavaScript (7 detection patterns) |
| 🖼️ **Embedded Assets** | Full support for base64-encoded images (`data:image/...`) |
| 📖 **Swagger UI** | Interactive API docs at `/apidocs` via [Flasgger](https://github.com/flasgger/flasgger) |
| 📡 **OpenTelemetry** | Distributed tracing with OTLP gRPC exporter |
| 📋 **Structured Logging** | JSON-formatted logs via [python-json-logger](https://github.com/madzak/python-json-logger) |
| 🐳 **Docker Ready** | Production-ready Dockerfile with Gunicorn |

## 🚀 Quick Start

### Prerequisites

- **Python 3.14+** and [uv](https://docs.astral.sh/uv/)
- WeasyPrint system dependencies (Pango, Cairo, GDK-Pixbuf)

### Local Development

```bash
# Clone the repository
git clone https://github.com/ZauJulio/pdf-render.git
cd pdf-render

# Install dependencies
uv sync --all-extras

# Configure environment
cp .env.example .env

# Run the server
uv run python -m app
```

The server starts at `http://localhost:5000` — Swagger UI at `http://localhost:5000/apidocs` 🎉

### 🐳 Docker

Pull the public image directly from **GitHub Container Registry**:

```bash
docker pull ghcr.io/zaujulio/weasyprint-pdf-render:latest
```

Run it:

```bash
docker run -d -p 5000:5000 ghcr.io/zaujulio/weasyprint-pdf-render:latest
```

Or use `docker compose`:

```bash
# From registry (no build needed)
docker compose up

# Build locally
docker compose up --build
```

> Multi-arch image available for `linux/amd64` and `linux/arm64`.

## 📡 API Usage

### `POST /api/v1/render`

Render HTML to PDF.

**Request:**

```json
{
  "html": "PGh0bWw+PGJvZHk+PGgxPkhlbGxvIFdvcmxkPC9oMT48L2JvZHk+PC9odG1sPg=="
}
```

> The `html` field is a **base64-encoded** HTML string.

**Response:**

```json
{
  "pdf": "JVBERi0xLjcK...",
  "metadata": {
    "pages": 1,
    "size_bytes": 12345,
    "rendering_time_ms": 150.5
  }
}
```

### `GET /health`

Health check endpoint — returns `{"status": "healthy"}`.

### Example with cURL

```bash
# Encode your HTML
HTML_B64=$(echo '<html><body><h1>Hello!</h1></body></html>' | base64 -w0)

# Render to PDF
curl -s -X POST http://localhost:5000/api/v1/render \
  -H "Content-Type: application/json" \
  -d "{\"html\": \"$HTML_B64\"}" | jq -r '.pdf' | base64 -d > output.pdf
```

## 🧪 Tests

The project has **56 tests** covering all modules with `pytest`:

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=app --cov-report=term-missing

# Run a specific test file
uv run pytest tests/test_sanitizer.py -v
```

### Test Coverage

| Module | Description | Tests |
| :--- | :--- | :---: |
| `test_config.py` | Configuration loading and defaults | 4 |
| `test_renderer.py` | PDF rendering with WeasyPrint | 7 |
| `test_routes.py` | API endpoints, validation, Swagger | 15 |
| `test_sanitizer.py` | Base64 decode, JS detection, HTML sanitization | 30 |

Coverage is automatically measured on every push via [GitHub Actions](.github/workflows/ci.yml) and reported to [Codecov](https://codecov.io/gh/ZauJulio/weasyprint-pdf-render).

## ⚙️ Configuration

All settings are loaded from environment variables (supports `.env` via [python-dotenv](https://github.com/theskumar/python-dotenv)):

| Variable | Default | Description |
| :--- | :--- | :--- |
| `FLASK_ENV` | `production` | Flask environment (`development` enables debug) |
| `LOG_LEVEL` | `INFO` | Logging level |
| `MAX_HTML_SIZE_MB` | `10` | Maximum HTML payload size in MB |
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `5000` | Server port |
| `OTEL_ENABLED` | `false` | Enable OpenTelemetry tracing |
| `OTEL_SERVICE_NAME` | `pdf-render` | Service name for traces |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://localhost:4317` | OTLP gRPC endpoint |

> See [.env.example](.env.example) for a ready-to-use template.

## 💡 Best Practices & WeasyPrint Tips

This service renders PDFs using **WeasyPrint**, which behaves differently than a browser like Chrome or a tool like Puppeteer.

### 🎨 CSS & Layout Limitations

* **CSS Grid / Flexbox:** Support is limited or experimental. For reliable layouts in PDFs, prefer using **tables** (`<table>`) or legacy block layouts.
- **JavaScript:** Scripts are **ignored** (and blocked by our API). All logic and dynamic rendering must be handled *before* sending the HTML.
- **Page Breaks:** Use CSS to control where pages split:

    ```css
    .keep-together { page-break-inside: avoid; }
    .new-page { page-break-before: always; }
    ```

### 🔤 Fonts & Assets

Since this service runs in an isolated container:
- **Custom Fonts:** System fonts aren't available. Use `@font-face` with **Base64** sources in your CSS.
- **Images:** Embed small images as Base64 (`data:image/png;base64,...`) to avoid network latency/errors.

### 🧩 HTML Templates (Handlebars)

We recommend generating the HTML string in your client application using a templating engine before calling this API. **Handlebars** is a great choice for this:

- **Node.js:** [Handlebars.js](https://handlebarsjs.com/)
- **C# / .NET:** [Handlebars.Net](https://github.com/Handlebars-Net/Handlebars.Net)
- **Java:** [Handlebars.java](https://github.com/jknack/handlebars.java)
- **Python:** [Jinja2](https://jinja.palletsprojects.com/) (Similar syntax)

## 🏗️ Project Structure

```
pdf-render/
├── app/
│   ├── __main__.py        # Entry point
│   ├── factory.py         # Flask app factory
│   ├── config.py          # Environment configuration
│   ├── routes.py          # API endpoints + Swagger specs
│   ├── renderer.py        # WeasyPrint PDF rendering
│   ├── sanitizer.py       # HTML validation & sanitization
│   ├── errors.py          # Custom exceptions & error handlers
│   ├── telemetry.py       # OpenTelemetry setup
│   ├── logging_config.py  # Structured JSON logging
│   └── swagger.py         # Swagger template & config
├── tests/
│   ├── conftest.py        # Pytest fixtures
│   ├── test_config.py
│   ├── test_renderer.py
│   ├── test_routes.py
│   └── test_sanitizer.py
├── .github/workflows/
│   └── ci.yml             # CI: lint, test, coverage, docker
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── .env.example
└── README.md
```

## 🛠️ Development

```bash
# Lint
uv run ruff check .

# Format
uv run ruff format .

# Type check
uv run ty check

# All checks
uv run ruff check . && uv run ruff format --check . && uv run pytest --cov=app
```

## 📄 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

---

<div align="center">

Made with 💜 by [ZauJulio](https://github.com/ZauJulio)

</div>
