from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.schemas.plant import CreatePlant, PlantResponse
from app.schemas.plant_event import CreatePlantEvent
from app.services.event_service import create_event, get_plant_events
from app.services.plant_service import (
    create_plant,
    get_plant_by_id,
    get_plants,
)


app = FastAPI(
    title="PlantBrain API",
    version="0.1.0",
)


def get_session():
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()


@app.get("/health")
def health_check():
    return {
        "status": "ok",
    }


@app.post("/plants", response_model=PlantResponse)
def create_plant_endpoint(
    data: CreatePlant,
    session: Session = Depends(get_session),
):
    plant = create_plant(
        session=session,
        data=data,
    )

    return plant


@app.get("/plants", response_model=list[PlantResponse])
def get_plants_endpoint(
    session: Session = Depends(get_session),
):
    return get_plants(session=session)


@app.get("/plants/{plant_id}", response_model=PlantResponse)
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


@app.get("/plants/{plant_id}/events")
def get_plant_events_endpoint(
    plant_id: int,
    session: Session = Depends(get_session),
):
    events = get_plant_events(
        session=session,
        plant_id=plant_id,
    )

    return [
        {
            "id": event.id,
            "plant_id": event.plant_id,
            "event_type": event.event_type,
            "occurred_at": event.occurred_at,
            "amount": event.amount,
            "unit": event.unit,
            "notes": event.notes,
        }
        for event in events
    ]