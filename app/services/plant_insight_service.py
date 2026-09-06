from sqlalchemy.orm import Session

from app.database.models import Plant
from app.schemas.plant_insight import (
    PatternInsightResponse,
    PlantInsightResponse,
    RecommendationResponse,
    WateringInsightResponse,
)
from app.services.care_analysis_service import (
    analyze_watering,
)
from app.services.care_pattern_service import (
    get_care_pattern,
)


def get_plant_insight(
    session: Session,
    plant_id: int,
) -> PlantInsightResponse:
    plant = session.get(
        Plant,
        plant_id,
    )

    if plant is None:
        raise ValueError(
            f"Plant with id {plant_id} not found"
        )

    watering_analysis = analyze_watering(
        session=session,
        plant_id=plant_id,
    )

    care_pattern = get_care_pattern(
        session=session,
        plant_id=plant_id,
    )

    watering_pattern = (
        care_pattern.event_types.get(
            "watering"
        )
    )

    pattern = PatternInsightResponse(
        regularity=(
            watering_pattern.regularity
            if watering_pattern
            else "insufficient_data"
        ),
        trend=(
            watering_pattern.trend
            if watering_pattern
            else "insufficient_data"
        ),
    )

    recommendation = _build_recommendation(
        watering_status=(
            watering_analysis.watering_status
        ),
        pattern=pattern,
    )

    watering = WateringInsightResponse(
        status=(
            watering_analysis.watering_status
        ),
        days_since_last_watering=(
            watering_analysis.days_since_last_watering
        ),
        average_interval_days=(
            watering_analysis.average_interval_days
        ),
        expected_next_watering_at=(
            watering_analysis.expected_next_watering_at
        ),
    )

    return PlantInsightResponse(
        plant_id=plant.id,
        plant_name=plant.name,
        watering=watering,
        pattern=pattern,
        recommendation=recommendation,
    )


def _build_recommendation(
    watering_status: str,
    pattern: PatternInsightResponse,
) -> RecommendationResponse:

    if watering_status == "overdue":
        return RecommendationResponse(
            action="water_now",
            priority="high",
            message=(
                "This plant is overdue "
                "for watering."
            ),
        )

    if watering_status == "due":
        return RecommendationResponse(
            action="water_soon",
            priority="medium",
            message=(
                "This plant will likely "
                "need watering soon."
            ),
        )

    if watering_status == "not_due":
        return RecommendationResponse(
            action="monitor",
            priority="low",
            message=(
                "Current watering pattern "
                "looks on schedule."
            ),
        )

    return RecommendationResponse(
        action="collect_more_data",
        priority="low",
        message=(
            "More care data is needed "
            "to generate recommendations."
        ),
    )