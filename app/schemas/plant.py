from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class CreatePlant(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)

    scientific_name: str | None = Field(
        default=None,
        max_length=150,
    )

    common_name: str | None = Field(
        default=None,
        max_length=150,
    )

    species: str | None = Field(
        default=None,
        max_length=150,
    )

    acquired_at: date | None = None

    location: str | None = Field(
        default=None,
        max_length=150,
    )

    status: str = Field(
        default="active",
        max_length=20,
    )

    notes: str | None = None


class UpdatePlant(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    scientific_name: str | None = Field(
        default=None,
        max_length=150,
    )

    common_name: str | None = Field(
        default=None,
        max_length=150,
    )

    species: str | None = Field(
        default=None,
        max_length=150,
    )

    acquired_at: date | None = None

    location: str | None = Field(
        default=None,
        max_length=150,
    )

    status: str | None = Field(
        default=None,
        max_length=20,
    )

    notes: str | None = None


class PlantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    scientific_name: str | None
    common_name: str | None
    species: str | None
    acquired_at: date | None
    location: str | None
    status: str
    notes: str | None