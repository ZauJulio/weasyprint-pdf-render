<div align="center">

# PDF Render Microservice

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

## Features

| Feature | Description |
| :--- | :--- |
| **Base64 I/O** | Receive HTML and return PDF as base64-encoded strings |
| **PDF Decode** | Decode base64 PDF back to downloadable file |
| **HTML Sanitization** | Strips scripts, event handlers, and unsafe tags via [bleach](https://github.com/mozilla/bleach) |
| **JS Detection** | Rejects HTML containing JavaScript (7 detection patterns) |
| **Embedded Assets** | Full support for base64-encoded images (`data:image/...`) |
| **API Key Auth** | Optional API key authentication with timing-safe comparison |
| **Rate Limiting** | Configurable per-endpoint rate limits via [Flask-Limiter](https://flask-limiter.readthedocs.io) |
| **CORS** | Configurable cross-origin resource sharing via [Flask-CORS](https://flask-cors.readthedocs.io) |
| **Security Headers** | CSP, HSTS, Referrer-Policy, Permissions-Policy via [Flask-Talisman](https://github.com/GoogleCloudPlatform/flask-talisman) |
| **Request Tracking** | Automatic `X-Request-ID` and `X-Response-Time` headers |
| **Swagger UI** | Interactive API docs at `/apidocs` via [Flasgger](https://github.com/flasgger/flasgger) |
| **OpenTelemetry** | Distributed tracing with OTLP gRPC exporter |
| **Structured Logging** | JSON-formatted logs via [python-json-logger](https://github.com/madzak/python-json-logger) |
| **Pydantic Validation** | Request/response validation with [Pydantic v2](https://docs.pydantic.dev) |
| **Docker Ready** | Multi-stage Alpine image with Gunicorn (`linux/amd64` + `linux/arm64`) |

## Quick Start

### Prerequisites

- **Python 3.14+** and [uv](https://docs.astral.sh/uv/)
- WeasyPrint system dependencies (Pango, Cairo, GDK-Pixbuf)

### Local Development

```bash
# Clone the repository
git clone https://github.com/ZauJulio/weasyprint-pdf-render.git
cd weasyprint-pdf-render

# Install dependencies
uv sync --all-extras

# Configure environment
cp .env.example .env

# Run the server
uv run python -m app
```

The server starts at `http://localhost:5000` -- Swagger UI at `http://localhost:5000/apidocs`.

### Docker

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

## API Usage

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

**Pipeline:** Validate JSON -> Decode base64 -> Check size limit -> Detect JavaScript -> Sanitize HTML -> Render PDF -> Return base64 + metadata.

### `POST /api/v1/decode/pdf`

Decode a base64-encoded PDF back to a downloadable file.

**Request:**

```json
{
  "pdf": "JVBERi0xLjcK..."
}
```

**Response:** Binary `application/pdf` file attachment (`decoded.pdf`).

### `GET /health`

Health check endpoint -- returns `{"status": "healthy", "service": "pdf-render"}`.

### Example with cURL

```bash
# Encode your HTML
HTML_B64=$(echo '<html><body><h1>Hello!</h1></body></html>' | base64 -w0)

# Render to PDF
curl -s -X POST http://localhost:5000/api/v1/render \
  -H "Content-Type: application/json" \
  -d "{\"html\": \"$HTML_B64\"}" | jq -r '.pdf' | base64 -d > output.pdf

# Decode a base64 PDF back to file
curl -s -X POST http://localhost:5000/api/v1/decode/pdf \
  -H "Content-Type: application/json" \
  -d "{\"pdf\": \"$(base64 -w0 output.pdf)\"}" -o decoded.pdf
```

### With API Key Authentication

```bash
# Set API_KEY in your .env, then pass it via header
curl -s -X POST http://localhost:5000/api/v1/render \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d "{\"html\": \"$HTML_B64\"}" | jq -r '.pdf' | base64 -d > output.pdf
```

## Error Handling

All errors follow a standardized JSON format:

```json
{
  "error": {
    "code": "JAVASCRIPT_DETECTED",
    "message": "HTML contains JavaScript which is not allowed.",
    "details": {}
  }
}
```

| Code | Status | Description |
| :--- | :---: | :--- |
| `INVALID_REQUEST` | 400 | Malformed request body |
| `VALIDATION_ERROR` | 422 | Pydantic validation failure |
| `HTML_REQUIRED` | 400 | Missing HTML field |
| `INVALID_BASE64` | 400 | Invalid base64 encoding |
| `HTML_TOO_LARGE` | 413 | HTML exceeds `MAX_HTML_SIZE_MB` |
| `JAVASCRIPT_DETECTED` | 400 | HTML contains JavaScript |
| `SANITIZATION_FAILED` | 400 | HTML sanitization error |
| `RENDER_FAILED` | 500 | WeasyPrint rendering failure |
| `UNSUPPORTED_MEDIA_TYPE` | 415 | Wrong `Content-Type` header |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `UNAUTHORIZED` | 401 | Invalid or missing API key |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

## Tests

The project has **152 tests** across 14 test files with `pytest`:

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
| `test_sanitizer.py` | Base64 decode, JS detection, HTML sanitization | 31 |
| `test_errors.py` | Custom exceptions and Flask error handlers | 22 |
| `test_routes.py` | API endpoints, validation, Swagger | 17 |
| `test_auth.py` | API key authentication (enabled/disabled) | 16 |
| `test_models.py` | Pydantic request/response models | 13 |
| `test_config.py` | Configuration loading and defaults | 9 |
| `test_renderer.py` | PDF rendering with WeasyPrint | 8 |
| `test_factory.py` | App factory, blueprints, middleware | 8 |
| `test_decode.py` | PDF decode endpoint | 7 |
| `test_security.py` | Security headers (CSP, HSTS, etc.) | 6 |
| `test_middleware.py` | Request ID and response time | 4 |
| `test_telemetry.py` | OpenTelemetry instrumentation | 4 |
| `test_rate_limit.py` | Rate limiting behavior | 3 |
| `test_cors.py` | CORS headers and preflight | 3 |

Coverage is automatically measured on every push via [GitHub Actions](.github/workflows/ci.yml) and reported to [Codecov](https://codecov.io/gh/ZauJulio/weasyprint-pdf-render).

## Configuration

All settings are loaded from environment variables (supports `.env` via [python-dotenv](https://github.com/theskumar/python-dotenv)):

### Application

| Variable | Default | Description |
| :--- | :--- | :--- |
| `FLASK_ENV` | `production` | Flask environment (`development` enables debug) |
| `LOG_LEVEL` | `INFO` | Logging level |
| `MAX_HTML_SIZE_MB` | `10` | Maximum HTML payload size in MB |
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `5000` | Server port |

### Authentication

| Variable | Default | Description |
| :--- | :--- | :--- |
| `API_KEY` | _(empty, disabled)_ | API key for authentication (empty = disabled) |
| `API_KEY_HEADER` | `X-API-Key` | Header name for the API key |

### CORS

| Variable | Default | Description |
| :--- | :--- | :--- |
| `CORS_ORIGINS` | `*` | Allowed origins (comma-separated) |
| `CORS_MAX_AGE` | `600` | Preflight cache max-age in seconds |

### Rate Limiting

| Variable | Default | Description |
| :--- | :--- | :--- |
| `RATE_LIMIT_ENABLED` | `true` | Enable rate limiting |
| `RATE_LIMIT_DEFAULT` | `60/minute` | Default rate limit |
| `RATE_LIMIT_RENDER` | `20/minute` | Render endpoint rate limit |

### Security

| Variable | Default | Description |
| :--- | :--- | :--- |
| `FORCE_HTTPS` | `false` | Force HTTPS redirects |

### OpenTelemetry

| Variable | Default | Description |
| :--- | :--- | :--- |
| `OTEL_ENABLED` | `false` | Enable OpenTelemetry tracing |
| `OTEL_SERVICE_NAME` | `pdf-render` | Service name for traces |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://localhost:4317` | OTLP gRPC endpoint |

> See [.env.example](.env.example) for a ready-to-use template.

## Best Practices & WeasyPrint Tips

This service renders PDFs using **WeasyPrint**, which behaves differently than a browser like Chrome or a tool like Puppeteer.

### CSS & Layout Limitations

* **CSS Grid / Flexbox:** Support is limited or experimental. For reliable layouts in PDFs, prefer using **tables** (`<table>`) or legacy block layouts.
- **JavaScript:** Scripts are **ignored** (and blocked by our API). All logic and dynamic rendering must be handled *before* sending the HTML.
- **Page Breaks:** Use CSS to control where pages split:

    ```css
    .keep-together { page-break-inside: avoid; }
    .new-page { page-break-before: always; }
    ```

### Fonts & Assets

Since this service runs in an isolated container:
- **Custom Fonts:** System fonts aren't available. Use `@font-face` with **Base64** sources in your CSS.
- **Images:** Embed small images as Base64 (`data:image/png;base64,...`) to avoid network latency/errors.

### HTML Templates (Handlebars)

We recommend generating the HTML string in your client application using a templating engine before calling this API. **Handlebars** is a great choice for this:

- **Node.js:** [Handlebars.js](https://handlebarsjs.com/)
- **C# / .NET:** [Handlebars.Net](https://github.com/Handlebars-Net/Handlebars.Net)
- **Java:** [Handlebars.java](https://github.com/jknack/handlebars.java)
- **Python:** [Jinja2](https://jinja.palletsprojects.com/) (Similar syntax)

## Project Structure

```
weasyprint-pdf-render/
├── app/
│   ├── __main__.py              # Entry point
│   ├── factory.py               # Flask app factory
│   ├── config.py                # Environment configuration
│   ├── errors.py                # Custom exceptions & error handlers
│   ├── swagger.py               # Swagger template & config
│   ├── extensions/
│   │   ├── auth.py              # API key authentication
│   │   ├── cors.py              # CORS configuration
│   │   ├── logging_config.py    # Structured JSON logging
│   │   ├── middleware.py        # Request ID & response timing
│   │   ├── rate_limit.py        # Rate limiting
│   │   ├── security.py          # Security headers (CSP, HSTS, etc.)
│   │   └── telemetry.py         # OpenTelemetry setup
│   ├── features/
│   │   ├── render/
│   │   │   ├── routes.py        # POST /api/v1/render
│   │   │   ├── models.py        # Pydantic models (request/response)
│   │   │   ├── service.py       # WeasyPrint PDF rendering
│   │   │   ├── sanitizer.py     # HTML validation & sanitization
│   │   │   └── docs.py          # Swagger specs
│   │   └── decode/
│   │       ├── routes.py        # POST /api/v1/decode/pdf
│   │       ├── models.py        # Pydantic models
│   │       ├── service.py       # Base64 PDF decode
│   │       └── docs.py          # Swagger specs
│   └── health/
│       ├── routes.py            # GET /health
│       └── docs.py              # Swagger specs
├── tests/
│   ├── conftest.py              # Pytest fixtures
│   ├── test_auth.py
│   ├── test_config.py
│   ├── test_cors.py
│   ├── test_decode.py
│   ├── test_errors.py
│   ├── test_factory.py
│   ├── test_middleware.py
│   ├── test_models.py
│   ├── test_rate_limit.py
│   ├── test_renderer.py
│   ├── test_routes.py
│   ├── test_sanitizer.py
│   ├── test_security.py
│   └── test_telemetry.py
├── scripts/
│   ├── generate_docs.py         # Swagger JSON + site generation
│   └── index.html               # Swagger UI for GitHub Pages
├── .github/workflows/
│   ├── ci.yml                   # CI: lint, type-check, test, docker
│   └── release.yml              # Auto tag + GitHub Release
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── .env.example
└── README.md
```

## Development

```bash
# Lint
uv run ruff check .

# Format
uv run ruff format .

# Type check
uv run ty check

# Run tests with coverage
uv run pytest --cov=app --cov-report=term-missing

# All checks (lint, format, type-check, test + coverage)
uv run task check
```

### Task Runner (taskipy)

| Task | Command | Description |
| :--- | :--- | :--- |
| `task dev` | `python -m app` | Run development server |
| `task lint` | `ruff check .` | Lint code |
| `task lint_fix` | `ruff check --fix .` | Lint and auto-fix |
| `task format` | `ruff format .` | Format code |
| `task format_check` | `ruff format --check .` | Check formatting |
| `task type` | `ty check` | Type check |
| `task test` | `pytest` | Run tests |
| `task cov` | `pytest --cov=app ...` | Run tests with coverage |
| `task check` | `lint_fix + format + type + cov` | Run all checks |
| `task docs` | `python scripts/generate_docs.py` | Generate API docs |

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

---

<div align="center">

Made with care by [ZauJulio](https://github.com/ZauJulio)

</div>
