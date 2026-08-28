from pydantic import BaseModel, ConfigDict, Field


class CreatePlace(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(
        min_length=1,
        max_length=100,
    )

    city: str | None = Field(
        default=None,
        max_length=100,
    )

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
    )

    timezone: str = Field(
        default="Asia/Tehran",
        min_length=1,
        max_length=100,
    )


class UpdatePlace(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    city: str | None = Field(
        default=None,
        max_length=100,
    )

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
    )

    timezone: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )


class PlaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    city: str | None
    latitude: float | None
    longitude: float | None
    timezone: str