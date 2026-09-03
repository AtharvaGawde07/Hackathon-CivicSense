"""
CivicAI — Centralised Application Constants

All issue types, status codes, severity levels, and category mappings
are defined here so that every module imports from a single source of truth.

When new civic-issue categories or AI models are added in later versions,
update this file and the rest of the application will pick up the changes.
"""

# ────────────────────────────────────────────────────────────
# Civic Issue Types (application-level)
# ────────────────────────────────────────────────────────────
ISSUE_TYPES: list[str] = [
    "Pothole",
    "Damaged Streetlight",
    "Overflowing Garbage",
    "Water Leakage",
    "Road Damage",
    "Other",
]

# ────────────────────────────────────────────────────────────
# Garbage Sub-categories (used by the garbage-classification model)
# ────────────────────────────────────────────────────────────
GARBAGE_SUBCATEGORIES: list[str] = [
    "Plastic",
    "Paper",
    "Glass",
    "Metal",
    "Organic",
    "E-Waste",
    "Mixed / Unknown",
]

# Mapping: garbage model label  →  application-level issue type
GARBAGE_MODEL_TO_ISSUE = "Overflowing Garbage"

# ────────────────────────────────────────────────────────────
# Complaint Statuses (full FSD 2 workflow, only "reported" used in V1)
# ────────────────────────────────────────────────────────────
STATUSES: list[str] = [
    "reported",
    "ai_verified",
    "assigned",
    "in_progress",
    "repair_completed",
    "ai_resolution_check",
    "citizen_confirmation",
    "resolved",
    "reopened",
]

# ────────────────────────────────────────────────────────────
# Priority Levels (not scored in V1, reserved for priority engine)
# ────────────────────────────────────────────────────────────
PRIORITY_LEVELS: dict[str, tuple[int, int]] = {
    "CRITICAL": (90, 100),
    "HIGH":     (70, 89),
    "MEDIUM":   (40, 69),
    "LOW":      (0,  39),
}

# ────────────────────────────────────────────────────────────
# Image Upload Settings
# ────────────────────────────────────────────────────────────
ALLOWED_IMAGE_EXTENSIONS: list[str] = ["jpg", "jpeg", "png"]
MAX_IMAGE_SIZE_MB: int = 10

# ────────────────────────────────────────────────────────────
# Report ID Prefix and Counter
# ────────────────────────────────────────────────────────────
REPORT_ID_PREFIX: str = "RPT"

# ────────────────────────────────────────────────────────────
# Model Directory
# ────────────────────────────────────────────────────────────
MODEL_DIR: str = "models"

# ────────────────────────────────────────────────────────────
# Data / Storage Paths
# ────────────────────────────────────────────────────────────
REPORTS_FILE: str = "data/reports.json"
UPLOADS_DIR: str = "uploads"
