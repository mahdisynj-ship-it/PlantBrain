# PlantBrain Architecture

This document describes the technical architecture and analytical data flow of PlantBrain v1.

PlantBrain is structured so that data storage, business logic, analytical logic, API delivery, and user-interface presentation remain separated.

---

## 1. System Architecture

```mermaid
flowchart TB
    UI["React Frontend<br/>Dashboard · Plant Detail · Visualizations"]

    API["FastAPI API Layer<br/>REST Endpoints"]

    PS["Plant & Place Services"]
    ES["Event Services"]
    WS["Weather Services"]
    CH["Care History Service"]
    CP["Care Pattern Service"]
    CA["Care Analysis Service"]
    IS["Plant Insight Service"]

    ORM["SQLAlchemy Models"]
    DB[("SQLite Database")]

    WEATHER["Open-Meteo API"]

    UI -->|"HTTP / JSON"| API

    API --> PS
    API --> ES
    API --> WS
    API --> CH
    API --> CP
    API --> IS

    IS --> CA
    IS --> CP

    PS --> ORM
    ES --> ORM
    WS --> ORM
    CH --> ORM
    CP --> ORM
    CA --> ORM

    WS -->|"Weather requests"| WEATHER

    ORM --> DB
```

### Layer Responsibilities

**React Frontend**

Presents the user-facing dashboard, plant-detail analytics, recommendations, and care visualizations.

**FastAPI API Layer**

Exposes REST endpoints and translates HTTP requests into service-layer operations.

**Service Layer**

Contains the application's business and analytical logic. This includes plant management, event processing, weather handling, historical statistics, care-pattern analysis, watering analysis, and insight generation.

**SQLAlchemy Models**

Represent persisted entities and relationships.

**SQLite**

Stores local PlantBrain data for v1.

**Open-Meteo**

Provides external weather data used by the weather layer.

---

## 2. Core Data Model

```mermaid
erDiagram
    PLACE ||--o{ PLANT : contains
    PLANT ||--o{ PLANT_EVENT : records
    PLANT_EVENT ||--o| WEATHER_SNAPSHOT : has

    PLACE {
        int id
        string name
        string city
        float latitude
        float longitude
        string timezone
    }

    PLANT {
        int id
        string name
        string scientific_name
        string species
        int place_id
        string status
    }

    PLANT_EVENT {
        int id
        int plant_id
        string event_type
        datetime occurred_at
        float amount
        string unit
    }

    WEATHER_SNAPSHOT {
        int id
        int event_id
        float temperature
        float humidity
        string condition
        datetime recorded_at
        string source
    }
```

The model intentionally separates plant identity, location context, care events, and environmental observations.

This allows analytical services to work from structured historical data rather than storing recommendations directly as source data.

---

## 3. Insight Data Flow

The central PlantBrain workflow transforms recorded care activity into an explainable recommendation.

```mermaid
flowchart TB
    P["Plant"]
    L["Place + Timezone"]
    E["Care Events"]
    W["Weather Context"]

    H["Care History<br/>Counts · Last activity · Intervals"]
    PAT["Care Pattern Analysis<br/>Regularity · Variability · Trend"]
    WA["Watering Analysis<br/>Average interval · Days since watering<br/>Expected next watering · Status"]
    INS["Plant Insight"]
    REC["Explainable Recommendation<br/>Action · Priority · Message"]
    FRONT["Dashboard + Plant Detail"]

    P --> H
    E --> H
    L --> H

    E --> PAT
    H --> PAT

    P --> WA
    E --> WA
    L --> WA

    W -.->|"Context available for future analysis"| INS

    PAT --> INS
    WA --> INS

    INS --> REC
    REC --> FRONT
```

---

## 4. Watering Analysis Pipeline

Watering is the primary analytical care type in PlantBrain v1.

```mermaid
flowchart LR
    A["Watering Events"]
    B["Sort by Time"]
    C["Calculate Intervals"]
    D["Average Interval"]
    E["Expected Next Watering"]
    F["Compare With Current Time"]
    G["Watering Status"]

    A --> B --> C --> D --> E --> F --> G

    G --> U["unknown"]
    G --> N["not_due"]
    G --> DUE["due"]
    G --> O["overdue"]
```

The system does not use a fixed universal watering schedule.

Instead, when enough data exists, it derives timing from the plant's own recorded watering history.

---

## 5. Care Pattern Analysis

PlantBrain analyzes the intervals between repeated care events.

```mermaid
flowchart TB
    EVENTS["Historical Care Events"]
    INTERVALS["Event Intervals"]

    AVG["Average Interval"]
    STD["Interval Standard Deviation"]
    TREND["Interval Trend"]

    REG["Regularity Classification"]
    TR["Trend Classification"]

    EVENTS --> INTERVALS

    INTERVALS --> AVG
    INTERVALS --> STD
    INTERVALS --> TREND

    AVG --> REG
    STD --> REG

    TREND --> TR
```

### Regularity States

```text
insufficient_data
regular
moderately_irregular
irregular
```

Regularity is based on interval variability relative to the average interval.

### Trend States

```text
insufficient_data
stable
increasing_interval
decreasing_interval
```

Trend analysis compares earlier and later care intervals to detect meaningful changes in care timing.

---

## 6. Insight Composition

The insight layer combines analytical outputs into a frontend-friendly representation.

```mermaid
flowchart LR
    WA["Watering Analysis"]
    CP["Care Pattern"]
    PI["Plant Insight"]
    R["Recommendation"]

    WA --> PI
    CP --> PI
    PI --> R
```

A simplified response looks like:

```json
{
  "watering": {
    "status": "due",
    "days_since_last_watering": 6.4,
    "average_interval_days": 6.0,
    "expected_next_watering_at": "..."
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

This API shape allows the frontend to present analytical results without duplicating the underlying analysis logic in React.

---

## 7. Timezone Strategy

Plant care happens in local time, while consistent data storage benefits from normalized timestamps.

PlantBrain therefore uses the following flow:

```mermaid
flowchart LR
    INPUT["Event Local Time"]
    TZ["Plant Place Timezone"]
    UTC["Normalize to UTC"]
    DB["Store UTC Timestamp"]
    READ["Read Event"]
    LOCAL["Convert to Local Context"]

    INPUT --> TZ --> UTC --> DB
    DB --> READ --> LOCAL
```

Naive incoming event timestamps are interpreted using the plant's place timezone.

Timezone-aware timestamps preserve their supplied offset before normalization.

Semantic event and weather timestamps are stored as UTC-normalized values and converted back to local time when local context is required.

---

## 8. Frontend Data Flow

The React frontend does not contain the analytical rules used to determine watering status or care patterns.

```mermaid
sequenceDiagram
    participant UI as React UI
    participant API as FastAPI
    participant Insight as Insight Service
    participant Analysis as Analysis Services
    participant DB as SQLite

    UI->>API: GET /plants
    API->>DB: Load plants
    DB-->>API: Plant records
    API-->>UI: Plant list

    UI->>API: GET /plants/{id}/insights
    API->>Insight: Build plant insight
    Insight->>Analysis: Analyze watering + patterns
    Analysis->>DB: Read care history
    DB-->>Analysis: Care events
    Analysis-->>Insight: Analytical results
    Insight-->>API: Insight response
    API-->>UI: JSON insight
    UI-->>UI: Render status + recommendation
```

For the plant-detail view, the frontend also requests care history, care patterns, and raw event data used for visualization.

---

## 9. Design Principles

PlantBrain v1 follows several architectural principles:

### Separate recorded data from derived insight

Events and weather observations are source data. Statuses, patterns, and recommendations are calculated from them.

### Keep analytical logic out of the UI

React presents results but does not determine watering status or care-pattern classifications.

### Keep API endpoints thin

Endpoints delegate domain behavior to dedicated service modules.

### Make recommendations explainable

A recommendation should be traceable to historical care data and analytical results.

### Preserve timezone context

Care activity is local by nature, so timezone handling is treated as part of the data model rather than only a presentation concern.

### Prefer deterministic portfolio behavior

The demo-data generator creates controlled care histories that exercise multiple analytical states.

---

## 10. V1 Boundary

PlantBrain v1 demonstrates:

```text
Data Collection
      ↓
Structured Storage
      ↓
Historical Analysis
      ↓
Pattern Detection
      ↓
Insight Generation
      ↓
Explainable Recommendation
      ↓
Responsive Presentation
```

It intentionally does not introduce machine learning, LLM-generated recommendations, IoT sensors, authentication, or production SaaS infrastructure.

The purpose of the architecture is to demonstrate a complete, understandable data-to-insight pipeline before adding unnecessary system complexity.