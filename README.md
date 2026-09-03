# 🏙️ CivicAI — Smart Civic Issue Reporting & Resolution Platform

> **Hackathon:** IGNITE IT 8.0  
> **Problem Statement:** FSD 2 — Smart Civic Issue Reporting & Resolution Platform  
> **Version:** 1.0 (Foundation)

---

## What is CivicAI?

CivicAI is a civic-technology platform that enables citizens to report urban infrastructure problems — potholes, damaged streetlights, overflowing garbage, water leakage, road damage, and more — using photographs and (in future versions) geolocation.

The platform is designed to eventually support the full FSD 2 lifecycle:

- AI-powered image classification  
- Duplicate-report clustering  
- Intelligent priority scoring  
- Authority assignment & tracking  
- After-repair verification  
- Spam/suspicious-report detection  
- Real-time status updates & dashboards  

---

## Current V1 Functionality

V1 is a **clean, extensible foundation**.  It implements:

| Feature | Status |
|---|---|
| Image upload & preview | ✅ Complete |
| AI classifier abstraction | ✅ Complete (placeholder mode) |
| AI prediction display | ✅ Complete |
| Category confirmation / manual selection | ✅ Complete |
| Optional description | ✅ Complete |
| Structured report creation | ✅ Complete |
| Local JSON persistence | ✅ Complete |
| Report summary display | ✅ Complete |

### ⚠️ Current AI Model Limitation

**V1 ships with no model file.**  The `models/` directory is intentionally empty.

A low-accuracy **garbage-classification model** will be connected later.  That model only detects *types of garbage* (Plastic, Paper, Glass, etc.) — it **cannot** detect potholes, streetlights, water leakage, or road damage.

When no model is present, the application gracefully falls back to manual category selection.  Nothing crashes.

---

## Supported Issue Types

All six categories are available for citizen selection in V1:

1. Pothole  
2. Damaged Streetlight  
3. Overflowing Garbage  
4. Water Leakage  
5. Road Damage  
6. Other  

Only **Overflowing Garbage** will have AI assistance once the garbage model is connected.

---

## Project Structure

```
CivicAI/
│
├── app.py                     # Streamlit entry-point
│
├── ai/
│   ├── __init__.py
│   ├── classifier.py          # CivicIssueClassifier (AI abstraction)
│   └── preprocessing.py       # Image preprocessing for model input
│
├── models/
│   └── .gitkeep               # EMPTY — place model files here
│
├── components/
│   ├── __init__.py
│   ├── upload.py              # Image upload & preview UI
│   └── report_form.py         # Category confirmation & description form
│
├── config/
│   ├── __init__.py
│   └── constants.py           # Centralised constants (issue types, statuses, paths)
│
├── utils/
│   ├── __init__.py
│   └── report.py              # Report creation & JSON persistence
│
├── data/
│   └── reports.json           # Local report storage (starts as [])
│
├── uploads/
│   └── .gitkeep               # Uploaded images saved here at runtime
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Architecture

```
Streamlit UI  (app.py)
    │
    ├── components/upload.py        → Image upload & validation
    ├── components/report_form.py   → Category + description form
    │
    ├── ai/classifier.py           → AI abstraction layer
    │       │
    │       └── ai/preprocessing.py → Model-specific image preprocessing
    │
    └── utils/report.py            → Report schema + JSON persistence
```

**Future expansion** (V2+):

```
ai/
├── classifier.py          ← garbage classification (+ general civic)
├── duplicate_detector.py   ← location + image similarity
├── priority_engine.py      ← scoring with proximity, age, severity
├── spam_detector.py        ← trust scoring
└── resolution_verifier.py  ← before/after image comparison
```

---

## Setup & Run

### 1. Clone the repository

```bash
git clone <repo-url>
cd CivicAI
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

- **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`
- **Windows (CMD):** `.venv\Scripts\activate.bat`
- **macOS / Linux:** `source .venv/bin/activate`

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
streamlit run app.py
```

The app will open at [http://localhost:8501](http://localhost:8501).

---

## How the AI Abstraction Works

### `ai/classifier.py` — `CivicIssueClassifier`

The classifier's `predict(image)` method always returns a **structured dict**:

```python
# When no model is loaded (V1 default):
{
    "available": False,
    "category": None,
    "confidence": 0.0,
    "probabilities": {},
    "model": None,
    "message": "No AI model is currently configured."
}

# When the garbage model is connected (future):
{
    "available": True,
    "category": "Plastic",
    "confidence": 0.72,
    "probabilities": {"Plastic": 0.72, "Paper": 0.12, ...},
    "model": "garbage_model",
    "message": None
}
```

The rest of the application only checks `result["available"]` to decide whether to show an AI suggestion or ask for manual input.  **No other file needs to change when the model is connected.**

### Where to place the model

1. Put your model file in `models/` (e.g. `models/garbage_model.h5`).
2. Open `ai/classifier.py` → `_load_model()`.
3. Uncomment / adapt the loading block for your framework.
4. Add the framework (e.g. `tensorflow`) to `requirements.txt`.
5. Update `ai/preprocessing.py` if the model needs specific input dimensions or normalisation.

---

## Report Schema

Every report follows the full FSD 2 schema, even in V1:

```jsonc
{
    "id": "RPT-000001",
    "issue":       { "type": "...", "subcategory": null },
    "image":       { "filename": "...", "path": "..." },
    "ai":          { "available": false, ... },
    "user":        { "confirmed_category": "...", "description": "..." },
    "location":    { "latitude": null, "longitude": null, "address": null },
    "status":      "reported",
    "priority":    { "score": null, "level": null, "factors": {} },
    "duplicates":  { "is_duplicate": null, "matches": [] },
    "spam":        { "score": null, "flagged": null, "reasons": [] },
    "resolution":  { "after_image": null, ... },
    "assignment":  { "authority_id": null, "department": null, ... },
    "created_at":  "...",
    "updated_at":  "..."
}
```

Fields marked `null` are reserved for future versions.

---

## Adding Future FSD 2 Modules

| Module | New files to create | Integration point |
|---|---|---|
| GPS / Map | `components/location.py` | Add to `app.py` between upload and form |
| Duplicate detection | `ai/duplicate_detector.py` | Call after `create_report()` |
| Priority engine | `ai/priority_engine.py` | Call after duplicate check |
| Spam detection | `ai/spam_detector.py` | Call during submission |
| Resolution verification | `ai/resolution_verifier.py` | New authority workflow page |
| Authority dashboard | `pages/authority.py` | Streamlit multi-page app |

---

## License

Hackathon project — IGNITE IT 8.0.
