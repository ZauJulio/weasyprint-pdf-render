"""Decode feature routes: base64 PDF decoding endpoint."""

from __future__ import annotations

import logging

from flasgger import swag_from
from flask import Blueprint, current_app, request
from pydantic import ValidationError as PydanticValidationError

from app.errors import (
    InvalidRequestError,
    UnsupportedMediaTypeError,
    ValidationError,
)
from app.extensions.rate_limit import limiter
from app.features.decode.docs import DECODE_SPEC
from app.features.decode.models import PdfDecodeRequest
from app.features.decode.service import decode_pdf_to_file

logger = logging.getLogger(__name__)

decode_bp = Blueprint("decode", __name__, url_prefix="/api/v1")


@decode_bp.route("/decode/pdf", methods=["POST"])
@limiter.limit(lambda: current_app.config.get("RATELIMIT_DEFAULT", "60/minute"))
@swag_from(DECODE_SPEC)
def decode_pdf():  # noqa: ANN202
    """Decode base64 PDF to file."""
    # Validate content type
    if not request.is_json:
        raise UnsupportedMediaTypeError

    # Parse request body
    data = request.get_json(silent=True)
    if data is None:
        raise InvalidRequestError

    # Validate with Pydantic
    try:
        decode_req = PdfDecodeRequest.model_validate(data)
    except PydanticValidationError as exc:
        raise ValidationError(
            details={"errors": exc.errors(include_url=False)},
        ) from exc

    # Delegate to service layer
    return decode_pdf_to_file(decode_req.pdf)
