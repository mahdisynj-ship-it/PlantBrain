from sqlalchemy.orm import Session

from app.database.models import Place
from app.schemas.place import CreatePlace, UpdatePlace


def create_place(
    session: Session,
    data: CreatePlace,
) -> Place:
    place = Place(
        name=data.name,
        city=data.city,
        latitude=data.latitude,
        longitude=data.longitude,
    )

    session.add(place)
    session.commit()
    session.refresh(place)

    return place


def get_places(
    session: Session,
) -> list[Place]:
    return (
        session.query(Place)
        .order_by(Place.id.desc())
        .all()
    )


def get_place_by_id(
    session: Session,
    place_id: int,
) -> Place | None:
    return session.get(Place, place_id)


def update_place(
    session: Session,
    place_id: int,
    data: UpdatePlace,
) -> Place | None:
    place = session.get(Place, place_id)

    if place is None:
        return None

    update_data = data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():
        setattr(place, field, value)

    session.commit()
    session.refresh(place)

    return place


def delete_place(
    session: Session,
    place_id: int,
) -> bool:
    place = session.get(Place, place_id)

    if place is None:
        return False

    session.delete(place)
    session.commit()

    return True