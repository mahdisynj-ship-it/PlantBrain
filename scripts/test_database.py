from datetime import datetime

from app.database.models import Plant, PlantEvent
from app.database.session import SessionLocal


def main():
    session = SessionLocal()

    try:
        plant = Plant(
            name="فیکوس اتاق خواب",
            scientific_name="Ficus elastica",
            common_name="Rubber Plant",
            species="Ficus elastica",
            location="اتاق خواب",
            status="active",
            notes="اولین گیاه ثبت‌شده در PlantBrain",
        )

        session.add(plant)
        session.flush()

        event = PlantEvent(
            plant_id=plant.id,
            event_type="watering",
            occurred_at=datetime.now(),
            amount=500,
            unit="ml",
            notes="اولین آبیاری ثبت‌شده",
        )

        session.add(event)
        session.commit()

        print("🌱 Plant created:")
        print(f"   ID: {plant.id}")
        print(f"   Name: {plant.name}")

        print("\n💧 Event created:")
        print(f"   ID: {event.id}")
        print(f"   Type: {event.event_type}")
        print(f"   Amount: {event.amount} {event.unit}")

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


if __name__ == "__main__":
    main()