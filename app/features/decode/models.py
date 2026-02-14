"""Pydantic models for the PDF decode feature."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PdfDecodeRequest(BaseModel):
    """Request body for the PDF decode endpoint."""

    pdf: str = Field(
        ...,
        min_length=1,
        description="Base64-encoded PDF string.",
        examples=["JVBERi0xLjcK"],
    )
