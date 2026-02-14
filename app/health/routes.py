"""Health feature routes: service health check endpoint."""

from __future__ import annotations

from flasgger import swag_from
from flask import Blueprint, jsonify

from app.health.docs import HEALTH_SPEC

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
@swag_from(HEALTH_SPEC)
def health_check():  # noqa: ANN202
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "pdf-render"})
