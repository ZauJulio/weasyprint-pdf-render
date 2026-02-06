# syntax=docker/dockerfile:1
# Check https://hub.docker.com/_/python for the latest sha256 digest
ARG PYTHON_VERSION=3.14
# Example using hash (SHA256 of python:3.14-alpine):
# FROM python:3.14-alpine@sha256:e84e... AS builder
FROM python:${PYTHON_VERSION}-alpine AS builder

# Install build dependencies
RUN apk add --no-cache \
    build-base \
    libffi-dev \
    musl-dev \
    gcc \
    python3-dev

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Install dependencies
# Copy only necessary files for dependency resolution to leverage cache
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# ------------------------------------------------------------------------------------
# Final Stage
# ------------------------------------------------------------------------------------
FROM python:${PYTHON_VERSION}-alpine AS runner

ARG UID=10001
ARG GID=10001

# Install runtime dependencies for WeasyPrint
# Note: explicit versions can be pinned for stability
RUN apk add --no-cache \
    pango \
    gdk-pixbuf \
    libffi \
    shared-mime-info \
    font-noto \
    ttf-dejavu \
    cairo \
    gobject-introspection \
    && fc-cache -f

# Create a non-privileged user
RUN addgroup -g ${GID} appuser && \
    adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid ${UID} \
    --ingroup appuser \
    appuser

WORKDIR /app

# Copy the environment from builder
COPY --from=builder /app/.venv /app/.venv

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY app /app/app
COPY scripts /app/scripts

USER appuser

# Expose port
EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health').read()" || exit 1

# Run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--timeout", "120", "--access-logfile", "-", "app.__main__:app"]
