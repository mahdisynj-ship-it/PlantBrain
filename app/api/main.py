import os

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.schemas.care_analysis import WateringAnalysisResponse
from app.schemas.care_history import CareHistoryResponse
from app.schemas.care_pattern import CarePatternResponse
from app.schemas.plant_insight import PlantInsightResponse
from app.schemas.place import (
    CreatePlace,
    PlaceResponse,
    UpdatePlace,
)
from app.schemas.plant import (
    CreatePlant,
    PlantResponse,
    UpdatePlant,
)
from app.schemas.plant_event import (
    CreatePlantEvent,
    PlantEventResponse,
    UpdatePlantEvent,
)
from app.schemas.weather_snapshot import (
    CreateWeatherSnapshot,
    UpdateWeatherSnapshot,
    WeatherSnapshotResponse,
)
from app.services.care_analysis_service import analyze_watering
from app.services.care_history_service import get_care_history
from app.services.care_pattern_service import get_care_pattern
from app.services.event_service import (
    create_event,
    delete_event,
    get_event_by_id,
    get_plant_events,
    update_event,
)
from app.services.event_weather_service import create_weather_for_event
from app.services.place_service import (
    create_place,
    delete_place,
    get_place_by_id,
    get_places,
    update_place,
)
from app.services.plant_insight_service import get_plant_insight
from app.services.plant_service import (
    create_plant,
    delete_plant,
    get_plant_by_id,
    get_plants,
    update_plant,
)
from app.services.weather_service import (
    create_weather_snapshot,
    delete_weather_snapshot,
    get_weather_snapshot_by_event_id,
    update_weather_snapshot,
)


# ---------------------------------------------------------
# Application
# ---------------------------------------------------------

app = FastAPI(
    title="PlantBrain API",
    version="0.1.0",
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

FRONTEND_ORIGIN = os.getenv(
    "PLANTBRAIN_FRONTEND_ORIGIN",
    "",
).strip().rstrip("/")

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

if FRONTEND_ORIGIN:
    ALLOWED_ORIGINS.append(FRONTEND_ORIGIN)


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Public Demo Protection
# ---------------------------------------------------------

DEMO_MODE = os.getenv(
    "PLANTBRAIN_DEMO_MODE",
    "",
).lower() in {
    "1",
    "true",
    "yes",
    "on",
}

READ_ONLY_METHODS = {
    "GET",
    "HEAD",
    "OPTIONS",
}


@app.middleware("http")
async def protect_public_demo(request, call_next):
    if DEMO_MODE and request.method not in READ_ONLY_METHODS:
        return JSONResponse(
            status_code=403,
            content={
                "detail": (
                    "PlantBrain public demo is read-only. "
                    "Data modifications are disabled."
                )
            },
        )

    return await call_next(request)


# ---------------------------------------------------------
# Database Session
# ---------------------------------------------------------

def get_session():
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()


# ---------------------------------------------------------
# Health
# ---------------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "ok",
    }


# ---------------------------------------------------------
# Plants
# ---------------------------------------------------------

@app.post(
    "/plants",
    response_model=PlantResponse,
)
def create_plant_endpoint(
    data: CreatePlant,
    session: Session = Depends(get_session),
):
    try:
        return create_plant(
            session=session,
            data=data,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


@app.get(
    "/plants",
    response_model=list[PlantResponse],
)
def get_plants_endpoint(
    session: Session = Depends(get_session),
):
    return get_plants(
        session=session,
    )


@app.get(
    "/plants/{plant_id}",
    response_model=PlantResponse,
)
def get_plant_endpoint(
    plant_id: int,
    session: Session = Depends(get_session),
):
    plant = get_plant_by_id(
        session=session,
        plant_id=plant_id,
    )

    if plant is None:
        raise HTTPException(
            status_code=404,
            detail=f"Plant with id {plant_id} not found",
        )

    return plant


@app.patch(
    "/plants/{plant_id}",
    response_model=PlantResponse,
)
def update_plant_endpoint(
    plant_id: int,
    data: UpdatePlant,
    session: Session = Depends(get_session),
):
    try:
        plant = update_plant(
            session=session,
            plant_id=plant_id,
            data=data,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    if plant is None:
        raise HTTPException(
            status_code=404,
            detail=f"Plant with id {plant_id} not found",
        )

    return plant


@app.get(
    "/plants/{plant_id}/analysis/watering",
    response_model=WateringAnalysisResponse,
)
def get_watering_analysis_endpoint(
    plant_id: int,
    session: Session = Depends(get_session),
):
    try:
        return analyze_watering(
            session=session,
            plant_id=plant_id,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


@app.get(
    "/plants/{plant_id}/care-history",
    response_model=CareHistoryResponse,
)
def get_care_history_endpoint(
    plant_id: int,
    period_days: int = 30,
    session: Session = Depends(get_session),
):
    try:
        return get_care_history(
            session=session,
            plant_id=plant_id,
            period_days=period_days,
        )
    except ValueError as error:
        message = str(error)

        if "not found" in message:
            raise HTTPException(
                status_code=404,
                detail=message,
            )

        raise HTTPException(
            status_code=422,
            detail=message,
        )


@app.get(
    "/plants/{plant_id}/care-pattern",
    response_model=CarePatternResponse,
)
def get_care_pattern_endpoint(
    plant_id: int,
    period_days: int = 90,
    session: Session = Depends(get_session),
):
    try:
        return get_care_pattern(
            session=session,
            plant_id=plant_id,
            period_days=period_days,
        )
    except ValueError as error:
        message = str(error)

        if "not found" in message:
            raise HTTPException(
                status_code=404,
                detail=message,
            )

        raise HTTPException(
            status_code=422,
            detail=message,
        )


@app.get(
    "/plants/{plant_id}/insights",
    response_model=PlantInsightResponse,
)
def get_plant_insight_endpoint(
    plant_id: int,
    session: Session = Depends(get_session),
):
    try:
        return get_plant_insight(
            session=session,
            plant_id=plant_id,
        )
    except ValueError as error:
        message = str(error)

        if "not found" in message:
            raise HTTPException(
                status_code=404,
                detail=message,
            )

        raise HTTPException(
            status_code=422,
            detail=message,
        )


@app.delete("/plants/{plant_id}")
def delete_plant_endpoint(
    plant_id: int,
    session: Session = Depends(get_session),
):
    deleted = delete_plant(
        session=session,
        plant_id=plant_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Plant with id {plant_id} not found",
        )

    return {
        "message": "Plant deleted successfully",
        "plant_id": plant_id,
    }


# ---------------------------------------------------------
# Plant Events
# ---------------------------------------------------------

@app.get(
    "/plants/{plant_id}/events",
    response_model=list[PlantEventResponse],
)
def get_plant_events_endpoint(
    plant_id: int,
    session: Session = Depends(get_session),
):
    return get_plant_events(
        session=session,
        plant_id=plant_id,
    )


@app.post(
    "/plants/{plant_id}/events",
    response_model=PlantEventResponse,
)
def create_plant_event_endpoint(
    plant_id: int,
    data: CreatePlantEvent,
    session: Session = Depends(get_session),
):
    try:
        return create_event(
            session=session,
            plant_id=plant_id,
            data=data,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


@app.get(
    "/plant-events/{event_id}",
    response_model=PlantEventResponse,
)
def get_event_endpoint(
    event_id: int,
    session: Session = Depends(get_session),
):
    event = get_event_by_id(
        session=session,
        event_id=event_id,
    )

    if event is None:
        raise HTTPException(
            status_code=404,
            detail=f"Event with id {event_id} not found",
        )

    return event


@app.patch(
    "/plant-events/{event_id}",
    response_model=PlantEventResponse,
)
def update_event_endpoint(
    event_id: int,
    data: UpdatePlantEvent,
    session: Session = Depends(get_session),
):
    event = update_event(
        session=session,
        event_id=event_id,
        data=data,
    )

    if event is None:
        raise HTTPException(
            status_code=404,
            detail=f"Event with id {event_id} not found",
        )

    return event


@app.delete("/plant-events/{event_id}")
def delete_event_endpoint(
    event_id: int,
    session: Session = Depends(get_session),
):
    deleted = delete_event(
        session=session,
        event_id=event_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Event with id {event_id} not found",
        )

    return {
        "message": "Event deleted successfully",
        "event_id": event_id,
    }


# ---------------------------------------------------------
# Weather Snapshots
# ---------------------------------------------------------

@app.post(
    "/plant-events/{event_id}/weather",
    response_model=WeatherSnapshotResponse,
)
def create_weather_snapshot_endpoint(
    event_id: int,
    data: CreateWeatherSnapshot,
    session: Session = Depends(get_session),
):
    try:
        return create_weather_snapshot(
            session=session,
            event_id=event_id,
            data=data,
        )
    except ValueError as error:
        message = str(error)

        if "not found" in message:
            raise HTTPException(
                status_code=404,
                detail=message,
            )

        raise HTTPException(
            status_code=409,
            detail=message,
        )


@app.post(
    "/plant-events/{event_id}/weather/auto",
    response_model=WeatherSnapshotResponse,
)
def create_automatic_weather_snapshot_endpoint(
    event_id: int,
    session: Session = Depends(get_session),
):
    try:
        return create_weather_for_event(
            session=session,
            event_id=event_id,
        )
    except ValueError as error:
        message = str(error)

        if "already exists" in message:
            raise HTTPException(
                status_code=409,
                detail=message,
            )

        raise HTTPException(
            status_code=404,
            detail=message,
        )


@app.get(
    "/plant-events/{event_id}/weather",
    response_model=WeatherSnapshotResponse,
)
def get_weather_snapshot_endpoint(
    event_id: int,
    session: Session = Depends(get_session),
):
    snapshot = get_weather_snapshot_by_event_id(
        session=session,
        event_id=event_id,
    )

    if snapshot is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Weather snapshot for event id "
                f"{event_id} not found"
            ),
        )

    return snapshot


@app.patch(
    "/plant-events/{event_id}/weather",
    response_model=WeatherSnapshotResponse,
)
def update_weather_snapshot_endpoint(
    event_id: int,
    data: UpdateWeatherSnapshot,
    session: Session = Depends(get_session),
):
    snapshot = update_weather_snapshot(
        session=session,
        event_id=event_id,
        data=data,
    )

    if snapshot is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Weather snapshot for event id "
                f"{event_id} not found"
            ),
        )

    return snapshot


@app.delete(
    "/plant-events/{event_id}/weather"
)
def delete_weather_snapshot_endpoint(
    event_id: int,
    session: Session = Depends(get_session),
):
    deleted = delete_weather_snapshot(
        session=session,
        event_id=event_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=(
                "Weather snapshot for event id "
                f"{event_id} not found"
            ),
        )

    return {
        "message": "Weather snapshot deleted successfully",
        "event_id": event_id,
    }


# ---------------------------------------------------------
# Places
# ---------------------------------------------------------

@app.post(
    "/places",
    response_model=PlaceResponse,
)
def create_place_endpoint(
    data: CreatePlace,
    session: Session = Depends(get_session),
):
    return create_place(
        session=session,
        data=data,
    )


@app.get(
    "/places",
    response_model=list[PlaceResponse],
)
def get_places_endpoint(
    session: Session = Depends(get_session),
):
    return get_places(
        session=session,
    )


@app.get(
    "/places/{place_id}",
    response_model=PlaceResponse,
)
def get_place_endpoint(
    place_id: int,
    session: Session = Depends(get_session),
):
    place = get_place_by_id(
        session=session,
        place_id=place_id,
    )

    if place is None:
        raise HTTPException(
            status_code=404,
            detail=f"Place with id {place_id} not found",
        )

    return place


@app.patch(
    "/places/{place_id}",
    response_model=PlaceResponse,
)
def update_place_endpoint(
    place_id: int,
    data: UpdatePlace,
    session: Session = Depends(get_session),
):
    place = update_place(
        session=session,
        place_id=place_id,
        data=data,
    )

    if place is None:
        raise HTTPException(
            status_code=404,
            detail=f"Place with id {place_id} not found",
        )

    return place


@app.delete("/places/{place_id}")
def delete_place_endpoint(
    place_id: int,
    session: Session = Depends(get_session),
):
    deleted = delete_place(
        session=session,
        place_id=place_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Place with id {place_id} not found",
        )

    return {
        "message": "Place deleted successfully",
        "place_id": place_id,
    }