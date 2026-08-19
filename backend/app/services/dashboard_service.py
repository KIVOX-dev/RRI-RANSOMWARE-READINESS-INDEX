"""D1 — Maturity Dashboard aggregation. Every field is read from
backend-computed, persisted state — nothing is computed fresh in the
frontend."""
from app.repositories.collections import evidence_repo, probe_runs_repo
from app.services import assessment_service, detection_service, dwell_time_service


def get_dashboard(assessment_id: str) -> dict:
    assessment = assessment_service.get_assessment(assessment_id)
    detection_matrix = detection_service.compute_detection_matrix(assessment_id)
    dwell_time = dwell_time_service.compute_dwell_time_readiness(assessment_id)

    evidence_count = evidence_repo.count({"assessment_id": assessment_id})
    latest_probe_runs = probe_runs_repo.find({"assessment_id": assessment_id}, sort=[("created_at", -1)], limit=1)
    probe_status = latest_probe_runs[0]["verification_status"] if latest_probe_runs else "not_run"

    return {
        "assessment": assessment,
        "detection_matrix": [d.model_dump() for d in detection_matrix],
        "dwell_time_readiness": dwell_time.model_dump(),
        "evidence_count": evidence_count,
        "probe_status": probe_status,
    }
