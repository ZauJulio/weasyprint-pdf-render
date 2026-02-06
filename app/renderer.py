"""PDF rendering service using WeasyPrint."""

from __future__ import annotations

import base64
import logging
import time
from dataclasses import dataclass, field

from weasyprint import HTML

from app.errors import RenderError

logger = logging.getLogger(__name__)


@dataclass
class RenderResult:
    """Result of a PDF rendering operation."""

    pdf_base64: str
    pages: int
    size_bytes: int
    rendering_time_ms: float
    metadata: dict[str, object] = field(default_factory=dict)


def render_html_to_pdf(html: str) -> RenderResult:
    """Render HTML content to a PDF document.

    Args:
        html: Sanitized HTML content.

    Returns:
        RenderResult with base64-encoded PDF and metadata.

    Raises:
        RenderError: If rendering fails.
    """
    logger.info("Rendering HTML to PDF")

    start_time = time.perf_counter()

    try:
        html_doc = HTML(string=html)
        document = html_doc.render()

        pdf_bytes = document.write_pdf()
        pages = len(document.pages)

    except Exception as exc:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.error("PDF rendering failed after %.2fms: %s", elapsed_ms, str(exc))
        raise RenderError(details={"reason": str(exc)}) from exc

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    pdf_base64 = base64.b64encode(pdf_bytes).decode("ascii")

    logger.info(
        "PDF rendered successfully: %d pages, %d bytes, %.2fms",
        pages,
        len(pdf_bytes),
        elapsed_ms,
    )

    return RenderResult(
        pdf_base64=pdf_base64,
        pages=pages,
        size_bytes=len(pdf_bytes),
        rendering_time_ms=round(elapsed_ms, 2),
    )
