"""
CivicAI — FastAPI Backend

Provides REST endpoints for civic-issue image analysis, report management,
and system health checks.

Run from the project root:
    uvicorn backend.main:app --reload
"""

from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from io import BytesIO
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Ensure the project root is on sys.path so that top-level packages
# (ai, utils, config) are importable when running via `uvicorn backend.main:app`.
# ---------------------------------------------------------------------------
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel, Field

from ai.classifier import CivicIssueClassifier
from config.constants import ALLOWED_IMAGE_EXTENSIONS, MAX_IMAGE_SIZE_MB
from utils.report import create_report, load_reports, save_report

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger("civicai.backend")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)

# ---------------------------------------------------------------------------
# Allowed MIME types (validated alongside the file extension)
# ---------------------------------------------------------------------------
_ALLOWED_CONTENT_TYPES: set[str] = {
    "image/jpeg",
    "image/png",
}

# ---------------------------------------------------------------------------
# Pydantic models for request validation
# ---------------------------------------------------------------------------


class LocationData(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    source: str = "browser_gps"
    accuracy_meters: float | None = None


class ReportRequest(BaseModel):
    """Body schema for ``POST /api/reports``."""

    issue_type: str
    ai_result: dict = Field(default_factory=dict)
    confirmed_category: str
    description: str = ""
    image_filename: str | None = None
    location: LocationData


# ---------------------------------------------------------------------------
# Application lifespan — initialise the classifier once at startup
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle hook."""
    logger.info("Initialising CivicIssueClassifier …")
    classifier = CivicIssueClassifier()
    app.state.classifier = classifier
    logger.info(
        "Classifier ready — models loaded: %s",
        classifier.loaded_models or "(none)",
    )
    yield
    logger.info("Shutting down CivicAI backend.")


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="CivicAI API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow front-end origins (ports 5500, 8000, 3000, local files, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


def _validate_image_upload(file: UploadFile, file_bytes: bytes) -> None:
    """Raise :class:`HTTPException` when the uploaded file is invalid.

    Checks performed:
    1. File extension is in ``ALLOWED_IMAGE_EXTENSIONS``.
    2. Content-Type header is an allowed image MIME type.
    3. File size does not exceed ``MAX_IMAGE_SIZE_MB``.
    """
    # --- Extension check ---
    filename = file.filename or ""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": (
                    f"Unsupported file extension '.{ext}'. "
                    f"Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
                ),
            },
        )

    # --- Content-Type check ---
    content_type = (file.content_type or "").lower()
    if content_type not in _ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": (
                    f"Unsupported content type '{content_type}'. "
                    f"Allowed: {', '.join(sorted(_ALLOWED_CONTENT_TYPES))}"
                ),
            },
        )

    # --- Size check ---
    max_bytes = MAX_IMAGE_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": (
                    f"File size ({len(file_bytes) / (1024 * 1024):.1f} MB) "
                    f"exceeds the {MAX_IMAGE_SIZE_MB} MB limit."
                ),
            },
        )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.post("/api/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """Accept an image upload, run AI classification, and return results."""
    try:
        file_bytes = await file.read()
    except Exception:
        logger.exception("Failed to read uploaded file")
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": "Could not read the uploaded file."},
        )

    # Validate extension, content-type, and size
    _validate_image_upload(file, file_bytes)

    # Attempt to open the image with PIL
    try:
        image = Image.open(BytesIO(file_bytes))
        image.verify()  # detect corrupted data
        # Re-open after verify (verify can leave the file pointer in a bad state)
        image = Image.open(BytesIO(file_bytes))
        image.load()  # force full decode
    except Exception:
        logger.exception("Uploaded file is not a valid image")
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "The uploaded file is corrupted or not a readable image.",
            },
        )

    # Run the classifier
    try:
        classifier: CivicIssueClassifier = app.state.classifier
        result: dict[str, Any] = classifier.predict(image)
    except Exception:
        logger.exception("AI classification failed")
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": "AI classification failed unexpectedly."},
        )

    # Strip non-serializable fields
    result.pop("annotated_image", None)
    result.pop("detections", None)

    # Rename 'available' → 'ai_available' and add success flag
    response: dict[str, Any] = {
        "success": True,
        "ai_available": result.pop("available", False),
        "category": result.get("category"),
        "subcategory": result.get("subcategory"),
        "confidence": result.get("confidence", 0.0),
        "probabilities": result.get("probabilities", {}),
        "model": result.get("model"),
        "message": result.get("message", ""),
    }
    return response


@app.post("/api/reports")
async def create_report_endpoint(body: ReportRequest):
    """Create and persist a new civic-issue report."""
    try:
        report = create_report(
            issue_type=body.issue_type,
            ai_result=body.ai_result,
            confirmed_category=body.confirmed_category,
            description=body.description,
            image_filename=body.image_filename,
            image_path=None,
            latitude=body.location.latitude,
            longitude=body.location.longitude,
            location_source=body.location.source,
            accuracy_meters=body.location.accuracy_meters,
        )
        save_report(report)
    except Exception:
        logger.exception("Failed to create / save report")
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": "Failed to save the report."},
        )

    return {
        "success": True,
        "report_id": report["id"],
        "status": report.get("status", "reported"),
    }


@app.get("/api/reports")
async def list_reports():
    """Return all stored reports."""
    try:
        reports = load_reports()
    except Exception:
        logger.exception("Failed to load reports")
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": "Failed to load reports."},
        )

    return {
        "success": True,
        "reports": reports,
        "count": len(reports),
    }


@app.get("/api/health")
async def health_check():
    """Simple health / readiness probe."""
    try:
        classifier: CivicIssueClassifier = app.state.classifier
        models = classifier.loaded_models
    except Exception:
        models = []

    return {
        "status": "ok",
        "models_loaded": models,
    }


# ---------------------------------------------------------------------------
# Serve frontend static assets (allows accessing the app directly on port 8000)
# ---------------------------------------------------------------------------
_frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if _frontend_dir.exists():
    from fastapi.staticfiles import StaticFiles

    app.mount("/", StaticFiles(directory=str(_frontend_dir), html=True), name="frontend")

