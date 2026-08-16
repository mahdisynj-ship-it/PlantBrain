from datetime import datetime

from pydantic import ValidationError

from app.schemas.plant import CreatePlant
from app.schemas.plant_event import CreatePlantEvent


def main():
    print("🌱 Valid plant input:")

    plant = CreatePlant(
        name="   فیکوس الاستیکا   ",
        scientific_name="Ficus elastica",
        location="اتاق خواب",
    )

    print(plant)
    print(f"Name after cleaning: '{plant.name}'")

    print("\n❌ Invalid plant input:")

    try:
        CreatePlant(name="")
    except ValidationError as error:
        print("Validation correctly failed:")
        print(error)

    print("\n💧 Valid event input:")

    event = CreatePlantEvent(
        plant_id=1,
        event_type="watering",
        occurred_at=datetime.now(),
        amount=500,
        unit="ml",
        notes="آبیاری معمولی",
    )

    print(event)

    print("\n❌ Invalid event input:")

    try:
        CreatePlantEvent(
            plant_id=1,
            event_type="watering",
            occurred_at=datetime.now(),
            amount=-500,
            unit="ml",
        )
    except ValidationError as error:
        print("Validation correctly failed:")
        print(error)


if __name__ == "__main__":
    main()