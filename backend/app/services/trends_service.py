"""D6 — Trend Analytics. Fewer than two completed assessments yields a real
empty state, never fabricated history."""
from app.models.benchmarking import TrendOut, TrendPoint
from app.repositories.collections import assessments_repo

MIN_HISTORY = 2


def get_trends(organisation_id: str) -> TrendOut:
    completed = assessments_repo.find(
        {"organisation_id": organisation_id, "status": "completed"}, sort=[("completed_at", 1)]
    )
    if len(completed) < MIN_HISTORY:
        return TrendOut(
            available=False,
            message=(
                f"Only {len(completed)} completed assessment(s) on record for this organisation. "
                f"At least {MIN_HISTORY} are needed to display a trend."
            ),
        )

    points = [
        TrendPoint(
            assessment_id=a["id"],
            completed_at=str(a["completed_at"]),
            maturity_score=a["maturity_score"] or 0,
            assurance_score=a["assurance_score"] or 0,
        )
        for a in completed
    ]
    return TrendOut(available=True, points=points, message="")
