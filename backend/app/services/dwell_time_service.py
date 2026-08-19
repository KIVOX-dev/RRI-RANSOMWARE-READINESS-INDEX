"""B4 — Dwell-Time Readiness. Presented strictly as a readiness indicator
derived from assessment signals — not a predictive model, not a probability."""
from app.models.detection import DwellTimeReadinessOut
from app.repositories.collections import answers_repo

DIMENSION_CONTROLS = {
    "credential_hygiene": ["IAM-MFA-ENFORCED", "IAM-PASSWORD-POLICY"],
    "password_reuse_signal": ["IAM-PASSWORD-REUSE-CONTROL"],
    "privilege_practices": ["IAM-LEAST-PRIVILEGE", "IAM-PRIVILEGED-SESSION-MONITORING"],
    "lateral_movement_exposure": ["NET-SEGMENTATION", "LOG-NETWORK-FLOW"],
}


def _dimension_score(answers_by_control: dict, control_ids: list[str]) -> float:
    scores = [answers_by_control[c]["score"] for c in control_ids if c in answers_by_control]
    if not scores:
        return 0.0
    return round((sum(scores) / len(scores)) * 20, 1)  # 0-5 -> 0-100


def compute_dwell_time_readiness(assessment_id: str) -> DwellTimeReadinessOut:
    answers = {a["control_id"]: a for a in answers_repo.find({"assessment_id": assessment_id})}

    dims = {name: _dimension_score(answers, controls) for name, controls in DIMENSION_CONTROLS.items()}
    overall = round(sum(dims.values()) / len(dims), 1) if dims else 0.0

    return DwellTimeReadinessOut(
        score=overall,
        credential_hygiene=dims["credential_hygiene"],
        password_reuse_signal=dims["password_reuse_signal"],
        privilege_practices=dims["privilege_practices"],
        lateral_movement_exposure=dims["lateral_movement_exposure"],
        explanation=(
            "Readiness indicator derived from assessment signals on credential hygiene, password reuse "
            "controls, privilege management practice, and lateral-movement exposure. This is not a "
            "predictive model and does not estimate an actual attacker dwell time."
        ),
    )
