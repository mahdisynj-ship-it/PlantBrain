from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, field_validator


def validate_timezone_name(
    value: str,
) -> str:
    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError as error:
        raise ValueError(
            "Invalid IANA timezone"
        ) from error

    return value


class CreatePlace(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

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

    @field_validator("timezone")
    @classmethod
    def validate_timezone(
        cls,
        value: str,
    ) -> str:
        return validate_timezone_name(
            value,
        )


class UpdatePlace(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

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

    @field_validator("timezone")
    @classmethod
    def validate_timezone(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        return validate_timezone_name(
            value,
        )


class PlaceResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    name: str
    city: str | None
    latitude: float | None
    longitude: float | None
    timezone: str