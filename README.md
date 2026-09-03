# 🏙️ CivicAI — Smart Civic Issue Reporting & Resolution Platform

> **Hackathon:** IGNITE IT 8.0
> **Problem Statement:** FSD 2 — Smart Civic Issue Reporting & Resolution Platform
> **Version:** 2.0 (HTML/FastAPI + Geolocation)

---

## What is CivicAI?

CivicAI is a civic-technology platform that enables citizens to report urban infrastructure problems — potholes, damaged streetlights, overflowing garbage, water leakage, road damage, and more — using photographs analysed by YOLO-based AI models.

The platform is designed to eventually support the full FSD 2 lifecycle: duplicate-report clustering, intelligent priority scoring, authority assignment & tracking, after-repair verification, spam detection, and real-time dashboards.

---

## Architecture

```
┌──────────────────────┐       HTTP / REST        ┌──────────────────────┐
│                      │  ───────────────────────▶ │                      │
│   HTML / CSS / JS    │  POST /api/analyze        │   FastAPI Backend    │
│   (frontend/)        │  POST /api/reports        │   (backend/main.py)  │
│                      │  GET  /api/reports         │                      │
│                      │  ◀─────────────────────── │                      │
└──────────────────────┘       JSON responses      └──────────┬───────────┘
                                                              │
                                                   ┌──────────▼───────────┐
                                                   │  AI Classifier       │
                                                   │  (ai/classifier.py)  │
                                                   │                      │
                                                   │  YOLO Models:        │
                                                   │  • garbage_class.    │
                                                   │  • road_damage       │
                                                   │  • litter_detection  │
                                                   │  • flood_detection   │
                                                   └──────────┬───────────┘
                                                              │
                                                   ┌──────────▼───────────┐
                                                   │  Report Layer        │
                                                   │  (utils/report.py)   │
                                                   │  → data/reports.json │
                                                   └──────────────────────┘
```

**Streamlit has been fully removed.** The frontend is plain HTML/CSS/JS; the backend is FastAPI. They communicate over REST.

---

## V1 Workflow

1. Citizen opens the **Detect** page and uploads an image (JPG/PNG).
2. The frontend `POST`s the image to `/api/analyze`.
3. The backend runs it through all loaded YOLO models and returns the highest-confidence prediction.
4. The frontend displays the AI suggestion (category + confidence).
5. The citizen confirms or overrides the category and adds a description.
6. The citizen uses the browser Geolocation API to capture their coordinates. If GPS fails, a manual coordinate fallback is displayed.
7. The citizen clicks **Submit Report**.
8. The frontend `POST`s the report (including location) to `/api/reports`; the backend stores it in `data/reports.json`.
9. The frontend displays the report ID.
10. The **Reports** page fetches all reports via `GET /api/reports`.

---

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/analyze` | Upload an image for AI classification |
| `POST` | `/api/reports` | Create a new civic-issue report |
| `GET`  | `/api/reports` | Retrieve all stored reports |
| `GET`  | `/api/health`  | System health + loaded models list |

### `POST /api/analyze`

**Request:** multipart/form-data with field `file` (JPG/JPEG/PNG, ≤10 MB)

**Success response:**
```json
{
  "success": true,
  "ai_available": true,
  "category": "Overflowing Garbage",
  "subcategory": "Plastic",
  "confidence": 0.72,
  "probabilities": { ... },
  "model": "garbage_classification",
  "message": "AI identified Overflowing Garbage (Plastic) with 72% confidence."
}
```

**Model unavailable response:**
```json
{
  "success": true,
  "ai_available": false,
  "category": null,
  "confidence": 0.0,
  "message": "No AI model is currently configured."
}
```

### `POST /api/reports`

**Request:** JSON body
```json
{
  "issue_type": "Overflowing Garbage",
  "confirmed_category": "Overflowing Garbage",
  "description": "Garbage overflow near bus stop",
  "image_filename": "photo.jpg",
  "ai_result": { "available": true, "category": "Overflowing Garbage", "confidence": 0.72 },
  "location": {
    "latitude": 19.0760,
    "longitude": 72.8777,
    "source": "browser_gps",
    "accuracy_meters": 12.5
  }
}
```

**Response:**
```json
{ "success": true, "report_id": "RPT-000001", "status": "reported" }
```

---

## Project Structure

```
CivicAI/
├── backend/
│   ├── __init__.py
│   └── main.py              # FastAPI app — all API routes
├── frontend/
│   ├── config.js             # API_BASE_URL (centralised)
│   ├── app.js                # Shared: theme, i18n, toast
│   ├── detect.html           # Upload + AI analysis + report form
│   ├── detect.js             # fetch calls to /api/analyze and /api/reports
│   ├── reports.html          # Live reports from /api/reports + map
│   ├── index.html            # Landing page
│   ├── issues.html           # Civic category reference
│   └── style.css             # Full design system
├── ai/
│   ├── __init__.py
│   ├── classifier.py         # CivicIssueClassifier (multi-model YOLO)
│   └── preprocessing.py      # Generic image preprocessing
├── models/
│   ├── garbage_classification/best.pt
│   ├── road_damage_detection/best.pt
│   ├── litter_detection/best.pt
│   ├── flood_detection/best.pt
│   └── (littering_event_detection/, ollama, whisper, yolo — available)
├── config/
│   ├── __init__.py
│   └── constants.py          # Issue types, statuses, paths
├── utils/
│   ├── __init__.py
│   └── report.py             # Report creation + JSON persistence
├── data/
│   └── reports.json          # Local report storage
├── uploads/
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Setup & Run

### 1. Clone and install

```bash
git clone <repo-url>
cd CivicAI
python -m venv .venv

# Activate:
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux:        source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Start the backend

```bash
python -m uvicorn backend.main:app --reload
```

Backend will be available at `http://127.0.0.1:8000`.
Check health: `http://127.0.0.1:8000/api/health`

### 3. Serve the frontend

Use any static file server. Examples:

```bash
# Python
python -m http.server 5500 --directory frontend

# VS Code Live Server (default port 5500)
# Or Node http-server
npx http-server frontend -p 5500
```

Open `http://127.0.0.1:5500/detect.html` to start.

---

## AI Model Status

| Model | Directory | Capability |
|-------|-----------|------------|
| Garbage Classification | `models/garbage_classification/best.pt` | Classifies types of garbage (low accuracy) |
| Road Damage Detection | `models/road_damage_detection/best.pt` | Detects road cracks, potholes (D00–D50 classes) |
| Litter Detection | `models/litter_detection/best.pt` | Detects litter/waste objects |
| Flood Detection | `models/flood_detection/best.pt` | Detects flooding/waterlogging |

> **Important:** These are pretrained models with varying accuracy. The garbage classifier in particular is known to be low-accuracy. The platform is honest about AI confidence — it always shows the confidence score and allows the citizen to override the category.

The application runs correctly even if *all* model files are missing — it falls back to manual category selection.

---

## Supported Issue Types

1. Pothole
2. Damaged Streetlight
3. Overflowing Garbage
4. Water Leakage
5. Road Damage
6. Other

AI currently assists with garbage, road damage, litter, and flood categories. Damaged Streetlight and Other require manual selection.

---

## Future FSD 2 Features

These fields exist in the report schema but have no logic yet:

| Feature | Reserved endpoint | Status |
|---------|-------------------|--------|
| GPS Location | `/api/reports` | ✅ Implemented (V2) |
| Duplicate Detection | `POST /api/duplicates/check` | Schema ready |
| Priority Scoring | `POST /api/priority/calculate` | Schema ready |
| Authority Dashboard | `GET /api/authority/reports` | Schema ready |
| Status Updates | `PATCH /api/reports/{id}/status` | Schema ready |
| Assignment | `POST /api/reports/{id}/assign` | Schema ready |
| Resolution Verification | `POST /api/reports/{id}/resolution` | Schema ready |
| Citizen Confirmation | `POST /api/reports/{id}/confirm` | Schema ready |
| Spam Detection | `POST /api/spam/check` | Schema ready |

---

## License

Hackathon project — IGNITE IT 8.0.
