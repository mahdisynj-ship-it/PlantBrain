from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.schemas.plant import CreatePlant, PlantResponse, UpdatePlant
from app.schemas.plant_event import CreatePlantEvent, PlantEventResponse
from app.services.event_service import create_event, get_plant_events
from app.services.plant_service import (
    create_plant,
    delete_plant,
    get_plant_by_id,
    get_plants,
    update_plant,
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
    return get_plants(
        session=session,
    )


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


@app.patch("/plants/{plant_id}", response_model=PlantResponse)
def update_plant_endpoint(
    plant_id: int,
    data: UpdatePlant,
    session: Session = Depends(get_session),
):
    plant = update_plant(
        session=session,
        plant_id=plant_id,
        data=data,
    )

    if plant is None:
        raise HTTPException(
            status_code=404,
            detail=f"Plant with id {plant_id} not found",
        )

    return plant


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