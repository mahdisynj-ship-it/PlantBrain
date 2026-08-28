from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.schemas.place import CreatePlace, PlaceResponse, UpdatePlace
from app.schemas.plant import CreatePlant, PlantResponse, UpdatePlant
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
            detail=f"Weather snapshot for event id {event_id} not found",
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
            detail=f"Weather snapshot for event id {event_id} not found",
        )

    return snapshot


@app.delete("/plant-events/{event_id}/weather")
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
            detail=f"Weather snapshot for event id {event_id} not found",
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