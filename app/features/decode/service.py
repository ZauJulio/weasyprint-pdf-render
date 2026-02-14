"""Decode feature service: base64 PDF decoding business logic."""

from __future__ import annotations

import io
import logging

from flask import Response, send_file

from app.features.render.sanitizer import decode_base64_to_bytes

logger = logging.getLogger(__name__)


def decode_pdf_to_file(encoded_pdf: str) -> Response:
    """Decode a base64-encoded PDF and return a file response.

    Args:
        encoded_pdf: Base64-encoded PDF string.

    Returns:
        Flask Response with the decoded PDF as an attachment.

    Raises:
        InvalidBase64Error: If the string is not valid base64.
    """
    logger.info("Decoding base64 PDF to file")

    pdf_bytes = decode_base64_to_bytes(encoded_pdf)

    logger.info("PDF decoded successfully: %d bytes", len(pdf_bytes))

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="decoded.pdf",
    )
