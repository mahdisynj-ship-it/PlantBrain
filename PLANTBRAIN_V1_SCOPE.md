# PlantBrain v1 Scope

## Project Goal

PlantBrain is a data-driven plant care system that transforms plant care records, location context, and weather data into explainable insights.

The goal of this version is to demonstrate:
- Backend engineering
- Data modeling
- External API integration
- Time-based data analysis
- Data visualization
- Product thinking
- UI/UX design

This is a portfolio project, not a production SaaS.

---

# Target Users

Primary:
- Plant enthusiasts
- People managing multiple plants

Future:
- Greenhouses
- Plant collections
- Professional growers

---

# Core Problem

Plant owners usually follow generic care schedules.

PlantBrain explores a different approach:

Instead of:
"Water every 7 days"

It asks:
"How does this specific plant behave over time?"

---

# Current Architecture

Plant
 |
 |-- Care Events
 |
 |-- Weather Context
 |
 |-- Care History
 |
 |-- Pattern Analysis
 |
 |-- Insights
 |
 |-- Dashboard


---

# Completed Features

## Plant Management

- Create plants
- Store plant information
- Associate plants with locations


## Location Context

- Latitude
- Longitude
- Timezone support


## Care Tracking

- Watering events
- Fertilizing events
- Event history


## Weather Integration

- Current weather
- Historical weather
- Open-Meteo integration


## Data Analysis

- Watering analysis
- Care history statistics
- Care pattern detection


## Engineering

- FastAPI backend
- SQLAlchemy ORM
- Alembic migrations
- Automated tests


---

# Version 1 Final Features

## 1. Plant Insights API

A single endpoint combining:

- Current care status
- Watering analysis
- Care pattern
- Recommendation


Example:

GET /plants/{id}/insights


---

## 2. Demo Dataset

Create realistic sample data:

Plants:
- Ficus
- Monstera
- Snake Plant


Include:
- Multiple care events
- Different watering patterns
- Weather context


---

## 3. Web Interface

Screens:

### Dashboard

Shows:
- Plant list
- Current status
- Quick insights


### Plant Detail

Shows:
- Plant information
- Care timeline
- Watering history


### Insights

Shows:
- Pattern
- Recommendation
- Explanation


---

## 4. Portfolio Presentation

Deliverables:

- GitHub repository
- README
- Architecture diagram
- Screenshots
- Case study page


---

# Out of Scope

Not included in v1:

- Authentication
- Multiple users
- Payments
- Mobile app
- IoT sensors
- Machine learning
- Disease detection
- Greenhouse management
- Real business deployment


---

# Success Criteria

PlantBrain v1 is complete when:

✓ Backend API works  
✓ Tests pass  
✓ UI demonstrates the product  
✓ GitHub explains the engineering  
✓ Portfolio case study tells the story  
