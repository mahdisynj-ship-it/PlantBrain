import pytest
from pydantic import ValidationError

from app.schemas.plant import CreatePlant, UpdatePlant
from app.services.plant_service import (
    create_plant,
    get_plant_by_id,
    get_plants,
    update_plant,
)


def test_create_plant(db_session):
    data = CreatePlant(
        name="فیکوس الاستیکا",
        scientific_name="Ficus elastica",
        common_name="Rubber Plant",
        location="اتاق خواب",
        status="active",
        notes="گیاه تست",
    )

    plant = create_plant(
        session=db_session,
        data=data,
    )

    assert plant.id is not None
    assert plant.name == "فیکوس الاستیکا"
    assert plant.scientific_name == "Ficus elastica"
    assert plant.common_name == "Rubber Plant"
    assert plant.location == "اتاق خواب"
    assert plant.status == "active"
    assert plant.notes == "گیاه تست"


def test_create_plant_rejects_empty_name():
    with pytest.raises(ValidationError):
        CreatePlant(
            name="",
        )


def test_create_plant_rejects_whitespace_only_name():
    with pytest.raises(ValidationError):
        CreatePlant(
            name="   ",
        )


def test_create_plant_service(db_session):
    data = CreatePlant(
        name="سانسوریا",
        scientific_name="Dracaena trifasciata",
        location="پذیرایی",
    )

    plant = create_plant(
        session=db_session,
        data=data,
    )

    assert plant.id is not None
    assert plant.name == "سانسوریا"
    assert plant.scientific_name == "Dracaena trifasciata"
    assert plant.location == "پذیرایی"
    assert plant.status == "active"


def test_get_plants(db_session):
    first = create_plant(
        session=db_session,
        data=CreatePlant(
            name="فیکوس",
        ),
    )

    second = create_plant(
        session=db_session,
        data=CreatePlant(
            name="سانسوریا",
        ),
    )

    plants = get_plants(
        session=db_session,
    )

    assert len(plants) == 2

    assert plants[0].id == first.id
    assert plants[1].id == second.id

    assert plants[0].name == "فیکوس"
    assert plants[1].name == "سانسوریا"


def test_get_plant_by_id(db_session):
    plant = create_plant(
        session=db_session,
        data=CreatePlant(
            name="زامیفولیا",
        ),
    )

    result = get_plant_by_id(
        session=db_session,
        plant_id=plant.id,
    )

    assert result is not None
    assert result.id == plant.id
    assert result.name == "زامیفولیا"


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
            name="فیکوس",
            location="اتاق خواب",
        ),
    )

    data = UpdatePlant(
        name="فیکوس الاستیکا",
        location="پذیرایی",
        notes="ویرایش شده",
    )

    updated = update_plant(
        session=db_session,
        plant_id=plant.id,
        data=data,
    )

    assert updated is not None
    assert updated.id == plant.id
    assert updated.name == "فیکوس الاستیکا"
    assert updated.location == "پذیرایی"
    assert updated.notes == "ویرایش شده"


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