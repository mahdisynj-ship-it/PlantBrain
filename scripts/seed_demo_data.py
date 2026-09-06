from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.database.models import (
    Place,
    Plant,
    PlantEvent,
    WeatherSnapshot,
)
from app.database.session import SessionLocal
from app.schemas.place import CreatePlace
from app.schemas.plant import CreatePlant
from app.schemas.plant_event import CreatePlantEvent
from app.schemas.weather_snapshot import (
    CreateWeatherSnapshot,
)
from app.services.event_service import create_event
from app.services.place_service import create_place
from app.services.plant_service import create_plant
from app.services.weather_service import (
    create_weather_snapshot,
)


DEMO_PREFIX = "[DEMO]"


def local_now(
    timezone_name: str,
) -> datetime:
    return datetime.now(
        ZoneInfo(timezone_name)
    ).replace(
        tzinfo=None,
        second=0,
        microsecond=0,
    )


def create_demo_event(
    session,
    plant_id: int,
    event_type: str,
    occurred_at: datetime,
    notes: str,
    amount: float | None = None,
    unit: str | None = None,
    temperature: float | None = None,
    humidity: float | None = None,
    weather_condition: str | None = None,
):
    event = create_event(
        session=session,
        plant_id=plant_id,
        data=CreatePlantEvent(
            event_type=event_type,
            occurred_at=occurred_at,
            notes=f"{DEMO_PREFIX} {notes}",
            amount=amount,
            unit=unit,
        ),
    )

    if (
        temperature is not None
        or humidity is not None
        or weather_condition is not None
    ):
        create_weather_snapshot(
            session=session,
            event_id=event.id,
            data=CreateWeatherSnapshot(
                temperature=temperature,
                humidity=humidity,
                weather_condition=(
                    weather_condition
                ),
                recorded_at=occurred_at,
                source="demo",
            ),
        )

    return event


def clear_demo_data(session):
    demo_events = (
        session.query(PlantEvent)
        .filter(
            PlantEvent.notes.like(
                f"{DEMO_PREFIX}%"
            )
        )
        .all()
    )

    for event in demo_events:
        session.delete(event)

    demo_plants = (
        session.query(Plant)
        .filter(
            Plant.notes.like(
                f"{DEMO_PREFIX}%"
            )
        )
        .all()
    )

    for plant in demo_plants:
        session.delete(plant)

    demo_places = (
        session.query(Place)
        .filter(
            Place.name.like(
                f"{DEMO_PREFIX}%"
            )
        )
        .all()
    )

    for place in demo_places:
        session.delete(place)

    session.commit()


def seed_places(session):
    lahijan = create_place(
        session=session,
        data=CreatePlace(
            name=f"{DEMO_PREFIX} Home",
            city="Lahijan",
            latitude=37.2073,
            longitude=50.0039,
            timezone="Asia/Tehran",
        ),
    )

    behshahr = create_place(
        session=session,
        data=CreatePlace(
            name=f"{DEMO_PREFIX} Studio",
            city="Behshahr",
            latitude=36.6923,
            longitude=53.5526,
            timezone="Asia/Tehran",
        ),
    )

    return lahijan, behshahr


def seed_plants(
    session,
    lahijan,
    behshahr,
):
    monstera = create_plant(
        session=session,
        data=CreatePlant(
            name="Monstera Deliciosa",
            scientific_name=(
                "Monstera deliciosa"
            ),
            common_name="Swiss Cheese Plant",
            species="Monstera deliciosa",
            location="Living Room",
            place_id=lahijan.id,
            status="active",
            notes=(
                f"{DEMO_PREFIX} "
                "Regular watering pattern."
            ),
        ),
    )

    ficus = create_plant(
        session=session,
        data=CreatePlant(
            name="Ficus Elastica",
            scientific_name=(
                "Ficus elastica"
            ),
            common_name="Rubber Plant",
            species="Ficus elastica",
            location="Bedroom",
            place_id=lahijan.id,
            status="active",
            notes=(
                f"{DEMO_PREFIX} "
                "Overdue watering example."
            ),
        ),
    )

    snake_plant = create_plant(
        session=session,
        data=CreatePlant(
            name="Snake Plant",
            scientific_name=(
                "Dracaena trifasciata"
            ),
            common_name="Snake Plant",
            species=(
                "Dracaena trifasciata"
            ),
            location="Studio Shelf",
            place_id=behshahr.id,
            status="active",
            notes=(
                f"{DEMO_PREFIX} "
                "Irregular watering pattern."
            ),
        ),
    )

    pothos = create_plant(
        session=session,
        data=CreatePlant(
            name="Golden Pothos",
            scientific_name=(
                "Epipremnum aureum"
            ),
            common_name="Golden Pothos",
            species="Epipremnum aureum",
            location="Desk",
            place_id=behshahr.id,
            status="active",
            notes=(
                f"{DEMO_PREFIX} "
                "Insufficient care data."
            ),
        ),
    )

    return (
        monstera,
        ficus,
        snake_plant,
        pothos,
    )


def seed_monstera(
    session,
    plant,
    now,
):
    watering_days = [
        24,
        18,
        12,
        6,
    ]

    for index, days_ago in enumerate(
        watering_days,
        start=1,
    ):
        create_demo_event(
            session=session,
            plant_id=plant.id,
            event_type="watering",
            occurred_at=(
                now - timedelta(
                    days=days_ago
                )
            ),
            notes=(
                f"Monstera watering "
                f"{index}"
            ),
            amount=500,
            unit="ml",
            temperature=24 + index * 0.3,
            humidity=68 - index,
            weather_condition="cloudy",
        )

    create_demo_event(
        session=session,
        plant_id=plant.id,
        event_type="fertilizing",
        occurred_at=(
            now - timedelta(days=20)
        ),
        notes="Monthly fertilizer",
        amount=5,
        unit="ml",
    )

    create_demo_event(
        session=session,
        plant_id=plant.id,
        event_type="pruning",
        occurred_at=(
            now - timedelta(days=15)
        ),
        notes="Removed damaged leaf",
    )


def seed_ficus(
    session,
    plant,
    now,
):
    watering_days = [
        30,
        24,
        18,
        12,
    ]

    for index, days_ago in enumerate(
        watering_days,
        start=1,
    ):
        create_demo_event(
            session=session,
            plant_id=plant.id,
            event_type="watering",
            occurred_at=(
                now - timedelta(
                    days=days_ago
                )
            ),
            notes=f"Ficus watering {index}",
            amount=400,
            unit="ml",
            temperature=25 + index * 0.2,
            humidity=64 - index,
            weather_condition="partly_cloudy",
        )

    create_demo_event(
        session=session,
        plant_id=plant.id,
        event_type="fertilizing",
        occurred_at=(
            now - timedelta(days=28)
        ),
        notes="Ficus fertilizer",
        amount=4,
        unit="ml",
    )


def seed_snake_plant(
    session,
    plant,
    now,
):
    watering_days = [
        45,
        39,
        22,
        5,
    ]

    for index, days_ago in enumerate(
        watering_days,
        start=1,
    ):
        create_demo_event(
            session=session,
            plant_id=plant.id,
            event_type="watering",
            occurred_at=(
                now - timedelta(
                    days=days_ago
                )
            ),
            notes=(
                f"Snake Plant watering "
                f"{index}"
            ),
            amount=250,
            unit="ml",
            temperature=26 + index * 0.2,
            humidity=58 - index,
            weather_condition="sunny",
        )

    create_demo_event(
        session=session,
        plant_id=plant.id,
        event_type="repotting",
        occurred_at=(
            now - timedelta(days=35)
        ),
        notes="Repotted into larger pot",
    )


def seed_pothos(
    session,
    plant,
    now,
):
    create_demo_event(
        session=session,
        plant_id=plant.id,
        event_type="watering",
        occurred_at=(
            now - timedelta(days=4)
        ),
        notes="First recorded watering",
        amount=300,
        unit="ml",
        temperature=25,
        humidity=67,
        weather_condition="cloudy",
    )


def print_summary(plants):
    print()
    print("PlantBrain demo data created.")
    print("--------------------------------")

    for plant in plants:
        print(
            f"{plant.id}: {plant.name}"
        )

    print("--------------------------------")
    print(
        "Run the API and inspect "
        "/docs or /plants/{id}/insights"
    )


def seed_demo_data():
    session = SessionLocal()

    try:
        print(
            "Removing previous demo data..."
        )
        clear_demo_data(session)

        print("Creating demo places...")
        lahijan, behshahr = seed_places(
            session
        )

        print("Creating demo plants...")
        (
            monstera,
            ficus,
            snake_plant,
            pothos,
        ) = seed_plants(
            session=session,
            lahijan=lahijan,
            behshahr=behshahr,
        )

        now = local_now(
            "Asia/Tehran"
        )

        print("Creating care history...")

        seed_monstera(
            session=session,
            plant=monstera,
            now=now,
        )

        seed_ficus(
            session=session,
            plant=ficus,
            now=now,
        )

        seed_snake_plant(
            session=session,
            plant=snake_plant,
            now=now,
        )

        seed_pothos(
            session=session,
            plant=pothos,
            now=now,
        )

        print_summary(
            [
                monstera,
                ficus,
                snake_plant,
                pothos,
            ]
        )

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


if __name__ == "__main__":
    seed_demo_data()

