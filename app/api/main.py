from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.schemas.plant import CreatePlant
from app.services.plant_service import create_plant
from app.schemas.plant_event import CreatePlantEvent
from app.services.event_service import create_event


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
        "service": "PlantBrain API",
    }


@app.post("/plants")
def create_plant_endpoint(
    data: CreatePlant,
    session: Session = Depends(get_session),
):
    plant = create_plant(
        session=session,
        data=data,
    )

    return {
        "id": plant.id,
        "name": plant.name,
        "scientific_name": plant.scientific_name,
        "location": plant.location,
        "status": plant.status,
    }
@app.post("/plants/{plant_id}/events")
def create_plant_event_endpoint(
    plant_id: int,
    data: CreatePlantEvent,
    session: Session = Depends(get_session),
):
    try:
        event = create_event(
            session=session,
            plant_id=plant_id,
            data=data,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    return {
        "id": event.id,
        "plant_id": event.plant_id,
        "event_type": event.event_type,
        "occurred_at": event.occurred_at,
        "amount": event.amount,
        "unit": event.unit,
        "notes": event.notes,
    }