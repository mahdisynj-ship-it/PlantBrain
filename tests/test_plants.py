import pytest
from pydantic import ValidationError

from app.schemas.plant import CreatePlant, UpdatePlant
from app.services.plant_service import (
    create_plant,
    get_plant_by_id,
    get_plants,
    update_plant,
)


def test_create_plant():
    data = CreatePlant(
        name="فیکوس تست",
        scientific_name="Ficus test",
        location="اتاق تست",
    )

    assert data.name == "فیکوس تست"
    assert isinstance(data, CreatePlant)


def test_create_plant_rejects_empty_name():
    with pytest.raises(ValidationError):
        CreatePlant(
            name="",
            scientific_name="Ficus test",
            location="اتاق تست",
        )


def test_create_plant_service(db_session):
    data = CreatePlant(
        name="فیکوس سرویس",
        scientific_name="Ficus elastica",
        location="اتاق تست",
        status="active",
    )

    plant = create_plant(
        session=db_session,
        data=data,
    )

    assert plant.id is not None
    assert plant.name == "فیکوس سرویس"
    assert plant.scientific_name == "Ficus elastica"
    assert plant.location == "اتاق تست"
    assert plant.status == "active"


def test_get_plants(db_session):
    first = create_plant(
        session=db_session,
        data=CreatePlant(
            name="گیاه اول",
            location="اتاق اول",
        ),
    )

    second = create_plant(
        session=db_session,
        data=CreatePlant(
            name="گیاه دوم",
            location="اتاق دوم",
        ),
    )

    plants = get_plants(
        session=db_session,
    )

    assert len(plants) == 2
    assert plants[0].id == first.id
    assert plants[0].name == "گیاه اول"
    assert plants[1].id == second.id
    assert plants[1].name == "گیاه دوم"


def test_get_plant_by_id(db_session):
    plant = create_plant(
        session=db_session,
        data=CreatePlant(
            name="گیاه برای جستجو",
            location="اتاق تست",
        ),
    )

    result = get_plant_by_id(
        session=db_session,
        plant_id=plant.id,
    )

    assert result is not None
    assert result.id == plant.id
    assert result.name == "گیاه برای جستجو"


def test_get_plant_by_id_returns_none_for_missing_plant(db_session):
    result = get_plant_by_id(
        session=db_session,
        plant_id=999,
    )

    assert result is None


def test_update_plant(db_session):
    plant = create_plant(
        session=db_session,
        data=CreatePlant(
            name="گیاه قبل از ویرایش",
            location="اتاق خواب",
            status="active",
        ),
    )

    data = UpdatePlant(
        name="گیاه بعد از ویرایش",
        location="پذیرایی",
    )

    updated = update_plant(
        session=db_session,
        plant_id=plant.id,
        data=data,
    )

    assert updated is not None
    assert updated.id == plant.id
    assert updated.name == "گیاه بعد از ویرایش"
    assert updated.location == "پذیرایی"
    assert updated.status == "active"


def test_update_plant_returns_none_for_missing_plant(db_session):
    data = UpdatePlant(
        location="پذیرایی",
    )

    result = update_plant(
        session=db_session,
        plant_id=999,
        data=data,
    )

    assert result is None