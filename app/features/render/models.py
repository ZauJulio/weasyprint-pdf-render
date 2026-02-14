"""Pydantic request/response models for the render feature."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RenderRequest(BaseModel):
    """Request body for the HTML-to-PDF render endpoint."""

    html: str = Field(
        ...,
        min_length=1,
        description="Base64-encoded HTML string.",
        examples=["PGh0bWw+PGJvZHk+PGgxPkhlbGxvIFdvcmxkPC9oMT48L2JvZHk+PC9odG1sPg=="],
    )


class RenderMetadata(BaseModel):
    """Metadata about a rendered PDF."""

    pages: int = Field(..., description="Number of pages in the PDF.")
    size_bytes: int = Field(..., description="Size of the PDF in bytes.")
    rendering_time_ms: float = Field(..., description="Time taken to render in milliseconds.")


class RenderResponse(BaseModel):
    """Response body for the HTML-to-PDF render endpoint."""

    pdf: str = Field(..., description="Base64-encoded PDF string.")
    metadata: RenderMetadata
