"""Render feature routes: HTML-to-PDF conversion endpoint."""

from __future__ import annotations

import logging

from flasgger import swag_from
from flask import Blueprint, current_app, jsonify, request
from pydantic import ValidationError as PydanticValidationError

from app.config import get_config
from app.errors import (
    InvalidRequestError,
    UnsupportedMediaTypeError,
    ValidationError,
)
from app.extensions.rate_limit import limiter
from app.features.render.docs import RENDER_SPEC
from app.features.render.models import RenderRequest
from app.features.render.sanitizer import validate_and_sanitize
from app.features.render.service import render_html_to_pdf

logger = logging.getLogger(__name__)

render_bp = Blueprint("render", __name__, url_prefix="/api/v1")


@render_bp.route("/render", methods=["POST"])
@limiter.limit(lambda: current_app.config.get("RATE_LIMIT_RENDER", "30/minute"))
@swag_from(RENDER_SPEC)
def render_pdf():  # noqa: ANN202
    """Render base64-encoded HTML to PDF."""
    config = get_config()

    # Validate content type
    if not request.is_json:
        raise UnsupportedMediaTypeError

    # Parse request body
    body = request.get_json(silent=True)
    if body is None:
        raise InvalidRequestError(details={"reason": "Request body must be valid JSON."})

    # Validate with Pydantic
    try:
        render_req = RenderRequest.model_validate(body)
    except PydanticValidationError as exc:
        raise ValidationError(
            details={"errors": exc.errors(include_url=False)},
        ) from exc

    # Validate, sanitize, and render
    sanitized_html = validate_and_sanitize(
        encoded_html=render_req.html,
        max_size_bytes=config.max_html_size_bytes,
        max_size_mb=config.MAX_HTML_SIZE_MB,
    )

    result = render_html_to_pdf(sanitized_html)

    logger.info(
        "Request completed: %d pages, %d bytes, %.2fms",
        result.pages,
        result.size_bytes,
        result.rendering_time_ms,
    )

    return jsonify(
        {
            "pdf": result.pdf_base64,
            "metadata": {
                "pages": result.pages,
                "size_bytes": result.size_bytes,
                "rendering_time_ms": result.rendering_time_ms,
            },
        }
    )
