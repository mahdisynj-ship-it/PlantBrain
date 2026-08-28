import pytest
from pydantic import ValidationError

from app.schemas.place import CreatePlace, UpdatePlace
from app.services.place_service import (
    create_place,
    delete_place,
    get_place_by_id,
    get_places,
    update_place,
)


def test_create_place_schema():
    data = CreatePlace(
        name="خانه",
        city="لاهیجان",
        latitude=37.2073,
        longitude=50.0039,
    )

    assert data.name == "خانه"
    assert data.city == "لاهیجان"
    assert data.latitude == 37.2073
    assert data.longitude == 50.0039


def test_create_place_rejects_empty_name():
    with pytest.raises(ValidationError):
        CreatePlace(
            name="",
        )


def test_create_place_rejects_invalid_latitude():
    with pytest.raises(ValidationError):
        CreatePlace(
            name="خانه",
            latitude=91,
        )


def test_create_place_rejects_invalid_longitude():
    with pytest.raises(ValidationError):
        CreatePlace(
            name="خانه",
            longitude=181,
        )


def test_create_place_service(db_session):
    place = create_place(
        session=db_session,
        data=CreatePlace(
            name="خانه",
            city="لاهیجان",
            latitude=37.2073,
            longitude=50.0039,
        ),
    )

    assert place.id is not None
    assert place.name == "خانه"
    assert place.city == "لاهیجان"
    assert place.latitude == 37.2073
    assert place.longitude == 50.0039


def test_get_places(db_session):
    first = create_place(
        session=db_session,
        data=CreatePlace(
            name="خانه",
        ),
    )

    second = create_place(
        session=db_session,
        data=CreatePlace(
            name="دفتر",
        ),
    )

    places = get_places(
        session=db_session,
    )

    assert len(places) == 2
    assert places[0].id == second.id
    assert places[1].id == first.id


def test_get_place_by_id(db_session):
    place = create_place(
        session=db_session,
        data=CreatePlace(
            name="خانه",
        ),
    )

    result = get_place_by_id(
        session=db_session,
        place_id=place.id,
    )

    assert result is not None
    assert result.id == place.id
    assert result.name == "خانه"


def test_get_place_by_id_returns_none_for_missing_place(db_session):
    result = get_place_by_id(
        session=db_session,
        place_id=999,
    )

    assert result is None


def test_update_place(db_session):
    place = create_place(
        session=db_session,
        data=CreatePlace(
            name="خانه قدیمی",
            city="لاهیجان",
        ),
    )

    updated = update_place(
        session=db_session,
        place_id=place.id,
        data=UpdatePlace(
            name="خانه",
            latitude=37.2073,
            longitude=50.0039,
        ),
    )

    assert updated is not None
    assert updated.id == place.id
    assert updated.name == "خانه"
    assert updated.city == "لاهیجان"
    assert updated.latitude == 37.2073
    assert updated.longitude == 50.0039


def test_update_missing_place(db_session):
    result = update_place(
        session=db_session,
        place_id=999,
        data=UpdatePlace(
            name="خانه",
        ),
    )

    assert result is None


def test_delete_place(db_session):
    place = create_place(
        session=db_session,
        data=CreatePlace(
            name="خانه",
        ),
    )

    deleted = delete_place(
        session=db_session,
        place_id=place.id,
    )

    assert deleted is True

    result = get_place_by_id(
        session=db_session,
        place_id=place.id,
    )

    assert result is None


def test_delete_missing_place(db_session):
    deleted = delete_place(
        session=db_session,
        place_id=999,
    )

    assert deleted is False