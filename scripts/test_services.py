from datetime import datetime

from app.database.session import SessionLocal
from app.schemas.plant import CreatePlant
from app.schemas.plant_event import CreatePlantEvent
from app.services.event_service import create_event
from app.services.plant_service import create_plant


def main():
    session = SessionLocal()

    try:
        plant_data = CreatePlant(
            name="فیکوس الاستیکا",
            scientific_name="Ficus elastica",
            common_name="Rubber Plant",
            location="اتاق خواب",
            notes="اولین گیاه واقعی PlantBrain",
        )

        plant = create_plant(
            session=session,
            data=plant_data,
        )

        event_data = CreatePlantEvent(
            plant_id=plant.id,
            event_type="watering",
            occurred_at=datetime.now(),
            amount=500,
            unit="ml",
            notes="آبیاری معمولی",
        )

        event = create_event(
            session=session,
            data=event_data,
        )

        print("🌱 Plant:")
        print(f"   ID: {plant.id}")
        print(f"   Name: {plant.name}")

        print("\n💧 Event:")
        print(f"   ID: {event.id}")
        print(f"   Type: {event.event_type}")
        print(f"   Amount: {event.amount} {event.unit}")

    finally:
        session.close()


if __name__ == "__main__":
    main()