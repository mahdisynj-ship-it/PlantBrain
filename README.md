# PlantBrain

**A data-driven plant care system that transforms care records, location context, and weather data into explainable insights.**

PlantBrain is a full-stack portfolio project built to explore how structured plant-care data can be turned into useful, understandable recommendations.

Instead of only storing watering and care records, PlantBrain analyzes care history, detects patterns, evaluates watering timing, and presents the results through a responsive dashboard.

---

## Overview

Most plant-care trackers focus on recording actions or sending fixed reminders.

PlantBrain explores a different approach:

> What if plant-care recommendations were based on the plant's own recorded history and context?

The system combines:

- plant information
- care events
- location and timezone context
- weather snapshots
- historical care intervals
- pattern analysis

to generate explainable plant-care insights.

The current version focuses primarily on **watering behavior** while maintaining a data model that can support multiple care-event types.

---

## What PlantBrain Does

PlantBrain currently supports:

- Plant and location management
- Plant care event tracking
- Weather snapshots associated with care events
- Timezone-aware event handling
- Historical care statistics
- Watering interval analysis
- Care-pattern detection
- Watering status classification
- Explainable recommendations
- Deterministic demo data
- Responsive dashboard and plant-detail views
- Data visualization of care activity and watering consistency
- REST API with automated test coverage

---

## From Raw Data to Insight

PlantBrain separates recorded facts from derived analysis.

```text
Plant
  │
  ├── Place / Timezone
  │
  ├── Care Events
  │      ├── Watering
  │      ├── Fertilizing
  │      ├── Pruning
  │      └── Repotting
  │
  └── Weather Context
          │
          ▼
     Care History
          │
          ▼
    Pattern Analysis
          │
          ▼
   Watering Analysis
          │
          ▼
       Insight
          │
          ▼
  Recommendation
          │
          ▼
      Dashboard
```

For example, watering records can be transformed into:

```text
Watering timestamps
        ↓
Intervals between watering events
        ↓
Average interval + variability
        ↓
Regularity + trend
        ↓
Current watering status
        ↓
Explainable recommendation
```

This makes the recommendation traceable back to recorded data rather than presenting it as an unexplained prediction.

---

## Dashboard

The dashboard provides a quick overview of the demo plant collection.

It summarizes plants into states such as:

- Needs attention
- On schedule
- Learning

Each plant card displays its current watering status, recent watering timing, average watering cycle, detected care pattern, and recommendation.

The interface consumes live data from the PlantBrain API rather than using hard-coded dashboard values.

---

## Plant Detail

Selecting a plant opens a detailed analytical view containing:

- current watering status
- days since last watering
- average watering interval
- expected next watering date
- recommendation priority
- care history
- activity breakdown
- watering interval history
- interval variability
- regularity classification
- watering trend

The UI is responsive and designed to work across desktop and mobile layouts.

---

## Care Analysis

### Watering Status

PlantBrain evaluates the current watering state using historical watering intervals.

Possible states include:

```text
unknown
not_due
due
overdue
```

When enough watering history exists, the system calculates an expected next watering time and compares the current time against that historical pattern.

### Care Regularity

Recorded intervals are analyzed for consistency.

Possible classifications include:

```text
insufficient_data
regular
moderately_irregular
irregular
```

### Interval Trend

PlantBrain also evaluates whether care intervals are changing over time.

Possible results include:

```text
insufficient_data
stable
increasing_interval
decreasing_interval
```

Together, these signals help distinguish the plant's current watering timing from its longer-term care pattern.

---

## Explainable Recommendations

PlantBrain converts analytical results into simple recommendations.

Examples include:

```text
water_now
water_soon
monitor
collect_more_data
```

Recommendations also include a priority and human-readable message.

For example:

```text
Status: overdue
Priority: high
Action: water_now

"This plant is overdue for watering based on its recent care pattern."
```

The goal is not to create an opaque prediction system, but to make the reasoning visible and understandable.

---

## Weather and Timezone Context

PlantBrain supports location-aware care records.

Each place can store:

- city
- latitude
- longitude
- IANA timezone

Internally, semantic event and weather timestamps are normalized to UTC before storage and converted back into the relevant local timezone when local context is required.

Weather snapshots can be associated with plant-care events, providing a foundation for future environmental analysis.

The current implementation includes an Open-Meteo weather provider.

---

## Architecture

PlantBrain uses a layered backend structure:

```text
React Frontend
      │
      │ HTTP / JSON
      ▼
FastAPI API Layer
      │
      ▼
Service Layer
      │
      ├── Plant Service
      ├── Event Service
      ├── Weather Service
      ├── Care History Service
      ├── Care Pattern Service
      ├── Care Analysis Service
      └── Plant Insight Service
      │
      ▼
SQLAlchemy Models
      │
      ▼
SQLite Database
```

The analysis logic lives in dedicated service modules instead of being embedded directly inside API endpoints or UI components.

---

## Backend Structure

```text
app/
├── api/
│   └── main.py
│
├── database/
│   ├── base.py
│   ├── session.py
│   └── models/
│       ├── place.py
│       ├── plant.py
│       ├── plant_event.py
│       └── weather_snapshot.py
│
├── schemas/
│   ├── care_analysis.py
│   ├── care_history.py
│   ├── care_pattern.py
│   ├── place.py
│   ├── plant.py
│   ├── plant_event.py
│   ├── plant_insight.py
│   └── weather_snapshot.py
│
├── services/
│   ├── care_analysis_service.py
│   ├── care_history_service.py
│   ├── care_pattern_service.py
│   ├── event_service.py
│   ├── event_weather_service.py
│   ├── open_meteo_provider.py
│   ├── place_service.py
│   ├── plant_insight_service.py
│   ├── plant_service.py
│   ├── weather_provider.py
│   └── weather_service.py
│
└── utils/
    └── datetime_utils.py
```

---

## Frontend Structure

```text
frontend/src/
├── api/
│   └── plantBrainApi.js
│
├── components/
│   └── CareVisualizations.jsx
│
├── App.jsx
├── App.css
├── index.css
└── main.jsx
```

The frontend retrieves plant and analytical data from the FastAPI backend and converts it into dashboard, detail, and visualization views.

---

## Tech Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- Alembic
- SQLite
- Pytest

### Frontend

- React
- Vite
- JavaScript
- CSS
- Recharts

### External Data

- Open-Meteo

---

## API

PlantBrain exposes REST endpoints for its core resources and analytical services.

Examples include:

```http
GET /plants
GET /plants/{plant_id}/events
GET /plants/{plant_id}/care-history
GET /plants/{plant_id}/care-pattern
GET /plants/{plant_id}/insights
```

A plant insight response combines several analytical layers into a frontend-friendly result.

Example:

```json
{
  "plant_id": 1,
  "plant_name": "Ficus",
  "watering": {
    "status": "due",
    "days_since_last_watering": 6.4,
    "average_interval_days": 6.0,
    "expected_next_watering_at": "2026-09-10T10:00:00"
  },
  "pattern": {
    "regularity": "regular",
    "trend": "stable"
  },
  "recommendation": {
    "action": "water_soon",
    "priority": "medium",
    "message": "This plant will likely need watering soon."
  }
}
```

FastAPI also provides interactive API documentation while the backend is running.

---

## Demo Data

PlantBrain includes a deterministic demo-data script:

```bash
python -m scripts.seed_demo_data
```

The demo dataset creates multiple plants with different care histories so the UI can demonstrate different analytical states.

Examples include plants with:

- regular watering patterns
- overdue watering
- irregular watering intervals
- insufficient historical data

Demo records are explicitly marked so they can be distinguished from other local data.

---

## Testing

The project includes automated tests covering API behavior, services, care analysis, pattern detection, weather handling, timezone conversion, plants, places, and events.

Current test suite:

```text
158 passed
```

Run the tests with:

```bash
pytest -q
```

---

## Running PlantBrain Locally

### 1. Clone the repository

```bash
git clone <repository-url>
cd PlantBrain
```

### 2. Create a Python virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install backend dependencies

```bash
pip install -e .
```

### 4. Apply database migrations

```bash
alembic upgrade head
```

### 5. Seed demo data

```bash
python -m scripts.seed_demo_data
```

### 6. Start the backend

```bash
python -m uvicorn app.api.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

### 7. Start the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at:

```text
http://localhost:5173
```

---

## Production Build

To create a frontend production build:

```bash
cd frontend
npm run build
```

---

## Project Scope

PlantBrain v1 is intentionally focused on demonstrating the complete path from structured data to analysis to user-facing insight.

The following features are intentionally outside the v1 scope:

- authentication
- multiple users
- payments
- notifications
- native mobile applications
- IoT sensors
- machine-learning models
- LLM-based recommendations
- disease detection
- greenhouse management
- social features

This scope keeps the project focused on data modeling, backend architecture, analytical logic, explainability, testing, and frontend presentation.

See [`PLANTBRAIN_V1_SCOPE.md`](PLANTBRAIN_V1_SCOPE.md) for the dedicated v1 scope document.

---

## Current Status

PlantBrain v1 currently includes:

- backend data model
- database migrations
- plant-care event tracking
- weather integration
- timezone-aware event processing
- care-history statistics
- care-pattern analysis
- watering analysis
- insight generation
- deterministic demo data
- responsive React dashboard
- plant-detail analytics
- care visualizations
- automated test suite

The remaining portfolio work focuses on documentation, architecture visuals, screenshots, and deployment.

---

## Project Goals

PlantBrain was built as a portfolio project to demonstrate work across:

- product thinking
- data modeling
- API design
- backend development
- analytical logic
- automated testing
- frontend development
- data visualization
- responsive UI design
- explainable data-driven decision support

The project emphasizes the reasoning between **data collection and user-facing recommendations**, not just the final interface.