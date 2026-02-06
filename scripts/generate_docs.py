"""Generate static documentation (Swagger JSON)."""

import json
import logging
import shutil
import sys
from pathlib import Path

# Add project root to sys.path to allow importing app
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.factory import create_app

logger = logging.getLogger(__name__)


def generate_swagger_json():
    """Generate swagger.json from Flask app."""
    app = create_app()
    client = app.test_client()

    # Flasgger usually serves specs at /apispec_1.json or similar,
    # but based on config it is at /apispec.json
    response = client.get("/apispec.json")

    if response.status_code == 200:
        # Define paths relative to this script or project root
        project_root = Path(__file__).resolve().parent.parent
        output_dir = project_root / "site"
        output_dir.mkdir(exist_ok=True)

        # Write swagger.json
        with (output_dir / "swagger.json").open("w") as f:
            json.dump(response.json, f, indent=2)

        logger.info("Generated site/swagger.json")

        # Copy index.html template
        source_index = project_root / "scripts" / "index.html"
        dest_index = output_dir / "index.html"

        if source_index.exists():
            shutil.copy(source_index, dest_index)
            logger.info("Copied index.html to site/")
        else:
            logger.info(f"Warning: Could not find {source_index}")

        # Copy coverage report if exists
        coverage_dir = project_root / "htmlcov"
        dest_coverage = output_dir / "coverage"
        if coverage_dir.exists():
            if dest_coverage.exists():
                shutil.rmtree(dest_coverage)

            shutil.copytree(coverage_dir, dest_coverage)
            logger.info("Copied coverage report to site/coverage")
        else:
            logger.info(f"Warning: Could not find coverage report at {coverage_dir}")
    else:
        logger.info(f"Failed to get swagger.json: {response.status_code}")
        exit(1)


if __name__ == "__main__":
    generate_swagger_json()
