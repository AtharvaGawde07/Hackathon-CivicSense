"""
CivicAI — Civic Issue Classifier (AI Abstraction)

Provides ``CivicIssueClassifier``, the single entry-point the rest of the
application uses to obtain AI predictions from YOLO models.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from config.constants import GARBAGE_SUBCATEGORIES, ISSUE_TYPES, MODEL_DIR

logger = logging.getLogger(__name__)


# ────────────────────────────────────────────────────────────
# Category and Subcategory Mappings
# ────────────────────────────────────────────────────────────
ROAD_DAMAGE_MAP = {
    "D00": ("Road Damage", "Longitudinal Crack (D00)"),
    "D10": ("Road Damage", "Transverse Crack (D10)"),
    "D20": ("Road Damage", "Alligator Crack (D20)"),
    "D40": ("Pothole", "Pothole (D40)"),
    "D43": ("Road Damage", "Crosswalk / Line Blur (D43)"),
    "D44": ("Road Damage", "Lane Line Blur (D44)"),
    "D50": ("Road Damage", "Manhole / Surface Patch (D50)"),
}


class CivicIssueClassifier:
    """Civic issue classifier supporting YOLO object detection models.

    Loads available models from the ``models/`` directory (e.g. garbage
    classification, road damage detection, flood detection, litter detection)
    and predicts civic issue categories with confidence scores and annotations.
    """

    def __init__(self) -> None:
        self._models: dict[str, Any] = {}
        self._labels: list[str] = GARBAGE_SUBCATEGORIES
        self._load_models()

    # ── Model Loading ────────────────────────────────────────

    def _load_models(self) -> None:
        """Scan and load all compatible models from the ``models/`` directory."""
        model_root = Path(MODEL_DIR)
        if not model_root.exists():
            return

        try:
            from ultralytics import YOLO
        except ImportError:
            logger.warning("ultralytics package not installed; running in manual fallback mode.")
            return

        # Known sub-model paths
        known_models = {
            "pothole": model_root / "pothole" / "best.pt",
            "garbage_classification": model_root / "garbage_classification" / "best.pt",
            "road_damage_detection": model_root / "road_damage_detection" / "best.pt",
            "flood_detection": model_root / "flood_detection" / "best.pt",
            "litter_detection": model_root / "litter_detection" / "best.pt",
        }

        loaded_paths = set()
        for model_name, path in known_models.items():
            if path.exists():
                try:
                    self._models[model_name] = YOLO(str(path))
                    loaded_paths.add(path.resolve())
                    logger.info("Loaded model: %s from %s", model_name, path)
                except Exception as e:
                    logger.error("Failed to load model %s (%s): %s", model_name, path, e)

        # Also discover any additional .pt files placed directly or in subdirectories
        for pt_path in model_root.rglob("*.pt"):
            if pt_path.resolve() in loaded_paths:
                continue
            stem = pt_path.parent.name if pt_path.name == "best.pt" else pt_path.stem
            if stem not in self._models:
                try:
                    self._models[stem] = YOLO(str(pt_path))
                    loaded_paths.add(pt_path.resolve())
                    logger.info("Discovered model: %s from %s", stem, pt_path)
                except Exception as e:
                    logger.error("Failed to load discovered model %s: %s", pt_path, e)

    # ── Public Interface ─────────────────────────────────────

    @property
    def is_available(self) -> bool:
        """``True`` when at least one usable model is loaded."""
        return len(self._models) > 0

    @property
    def loaded_models(self) -> list[str]:
        """List of currently loaded model identifiers."""
        return list(self._models.keys())

    def predict(self, image: Image.Image, conf_threshold: float = 0.20) -> dict:
        """Analyse an uploaded civic-issue image using loaded AI models.

        Parameters
        ----------
        image:
            A PIL Image of the reported civic issue.
        conf_threshold:
            Minimum confidence required to accept a detection (default 0.20).

        Returns
        -------
        dict
            A structured prediction result containing:
            * ``available`` — whether model(s) produced this result
            * ``category`` — top-level application issue type (e.g. "Pothole")
            * ``subcategory`` — specific detected class (e.g. "Pothole (D40)", "Plastic")
            * ``confidence`` — 0.0–1.0 confidence score
            * ``probabilities`` — confidence distribution or detected class scores
            * ``model`` — model identifier that produced the best detection
            * ``message`` — human-readable prediction status
            * ``annotated_image`` — PIL Image with bounding boxes drawn (if detected)
            * ``detections`` — list of all detected objects
        """
        if not self.is_available:
            return self._no_model_result()

        all_detections: list[dict] = []
        annotated_image: Image.Image | None = None
        best_detection: dict | None = None
        best_conf: float = 0.0

        for model_name, model in self._models.items():
            try:
                results = model(image, conf=conf_threshold, verbose=False)
                if not results:
                    continue

                res = results[0]
                boxes = res.boxes

                if boxes is not None and len(boxes) > 0:
                    names = res.names
                    for box in boxes:
                        cls_id = int(box.cls.item())
                        conf = float(box.conf.item())
                        class_name = names.get(cls_id, str(cls_id))

                        issue_type, subcategory = self._map_to_issue_type(model_name, class_name)

                        det = {
                            "model": model_name,
                            "class_name": class_name,
                            "issue_type": issue_type,
                            "subcategory": subcategory,
                            "confidence": round(conf, 4),
                            "box": [float(x) for x in box.xyxy[0].tolist()] if box.xyxy is not None else [],
                        }
                        all_detections.append(det)

                        if conf > best_conf:
                            best_conf = conf
                            best_detection = det
                            # Generate annotated preview image from best model
                            try:
                                bgr_array = res.plot()
                                annotated_image = Image.fromarray(bgr_array[..., ::-1])
                            except Exception:
                                annotated_image = None
            except Exception as e:
                logger.error("Inference failed for model %s: %s", model_name, e)

        if best_detection is not None and best_conf >= conf_threshold:
            # Aggregate probabilities / class scores
            probabilities: dict[str, float] = {}
            for d in all_detections:
                key = f"{d['issue_type']} ({d['subcategory']})"
                probabilities[key] = max(probabilities.get(key, 0.0), d["confidence"])

            category = best_detection["issue_type"]
            subcategory = best_detection["subcategory"]

            return {
                "available": True,
                "category": category,
                "subcategory": subcategory,
                "confidence": round(best_conf, 4),
                "probabilities": probabilities,
                "model": best_detection["model"],
                "message": f"AI identified **{category}** ({subcategory}) with {int(best_conf * 100)}% confidence.",
                "annotated_image": annotated_image,
                "detections": all_detections,
            }

        # Fallback when models ran but no detections exceeded the confidence threshold
        return {
            "available": False,
            "category": None,
            "subcategory": None,
            "confidence": 0.0,
            "probabilities": {},
            "model": list(self._models.keys())[0] if self._models else None,
            "message": "No civic issue detected with sufficient confidence in this image. Please select the category manually.",
            "annotated_image": None,
            "detections": [],
        }

    # ── Helpers ──────────────────────────────────────────────

    def _map_to_issue_type(self, model_name: str, class_name: str) -> tuple[str, str]:
        """Map model-specific class name to top-level issue category and subcategory."""
        # 1. Pothole model
        if "pothole" in model_name or class_name.lower() == "pothole":
            return ("Pothole", "Pothole")

        # 2. Road damage model
        if "road_damage" in model_name or class_name.upper() in ROAD_DAMAGE_MAP:
            mapping = ROAD_DAMAGE_MAP.get(class_name.upper())
            if mapping:
                return mapping
            return ("Road Damage", class_name)

        # 2. Flood / water logging model
        if "flood" in model_name:
            if "flood" in class_name.lower() or "water" in class_name.lower():
                return ("Water Leakage", f"Flooding / {class_name.title()}")
            return ("Water Leakage", class_name)

        # 3. Garbage / Litter models
        if "garbage" in model_name or "litter" in model_name:
            clean_sub = class_name.replace("_", " ").title()
            return ("Overflowing Garbage", clean_sub)

        # Default fallback
        clean_class = class_name.replace("_", " ").title()
        if clean_class in ISSUE_TYPES:
            return (clean_class, clean_class)

        return ("Other", clean_class)

    @staticmethod
    def _no_model_result() -> dict:
        """Return the standard "no model loaded" result."""
        return {
            "available": False,
            "category": None,
            "subcategory": None,
            "confidence": 0.0,
            "probabilities": {},
            "model": None,
            "message": "No AI model is currently configured. Please select the issue category manually.",
            "annotated_image": None,
            "detections": [],
        }
