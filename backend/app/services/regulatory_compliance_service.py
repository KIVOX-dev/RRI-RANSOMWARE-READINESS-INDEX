"""Computed, per-framework regulatory compliance verdicts — the "does this
actually work, not just display" layer on top of regulatory_service.py's
static citations. Every requirement below is backed by a real, existing
assessment control (see app/seed/questions_data.py's INDIAN_REGULATORY_CONTEXT
for the citation each one is drawn from) or, where a better real signal
exists, a measured value instead of a self-reported answer:

- Log retention: CERT-In's actual requirement is >=180 days, but the
  self-reported control LOG-006 only asks "meets or exceeds 90 days" — so
  this checks the real, numeric `log_sources.retention_days` field (from the
  Log Gaps feature) against 180 directly, rather than trusting the weaker
  self-reported boolean.
- NTP sync: PROBE-NTP-SYNC carries a real probe_check_id (CHECK_006) — if the
  organisation has run the verification probe, this checks the actual signed
  probe result instead of the self-reported answer.

Everything else is a self-reported boolean/select control, same as every
other control in the assessment — "met" means "answered affirmatively",
not independently verified. The verdict is a factual statement about what
the assessment data shows, not a legal audit — see DISCLAIMER.
"""
from app.repositories.collections import answers_repo, log_sources_repo, probe_checks_repo, probe_runs_repo
from app.models.regulatory import FrameworkComplianceOut, RegulatoryComplianceOut, RequirementOut

DISCLAIMER = (
    "Computed from this assessment's self-reported answers (and, where available, "
    "verification-probe results and configured log retention) — not a legal compliance "
    "audit. Confirm current obligations with qualified legal/compliance counsel."
)

CERT_IN_LOG_RETENTION_DAYS = 180

FRAMEWORKS: dict[str, dict] = {
    "CERT-In Directions, 2022": {
        "url": "https://www.cert-in.org.in/",
        "requirements": [
            {
                "key": "incident_reporting_readiness",
                "description": "Documented incident-reporting readiness for CERT-In's 6-hour notification window (checklist, contact points, and internal escalation triggers).",
                "control_ids": ["COMP-002", "IR-006", "IR-011"],
                "basis": "self_reported",
            },
            {
                "key": "log_retention_180d",
                "description": f"Log retention meets CERT-In's {CERT_IN_LOG_RETENTION_DAYS}-day minimum (checked against configured log source retention, not the assessment's own 90-day control, which is a lower bar).",
                "control_ids": [],
                "basis": "measured_threshold",
            },
            {
                "key": "ntp_sync",
                "description": "Systems synchronize time from a trusted NTP source.",
                "control_ids": ["PROBE-NTP-SYNC"],
                "basis": "technical_probe",
            },
            {
                "key": "reporting_rehearsed",
                "description": "Incident reporting workflow rehearsed via tabletop exercise.",
                "control_ids": ["COMP-010"],
                "basis": "self_reported",
            },
        ],
    },
    "DPDP Act, 2023": {
        "url": "https://www.meity.gov.in/data-protection-framework",
        "requirements": [
            {"key": "general_awareness", "description": "Awareness of sector-relevant data-handling obligations is maintained.", "control_ids": ["COMP-001"], "basis": "self_reported"},
            {"key": "data_availability_bcp", "description": "Data availability risk is explicitly considered in business continuity planning.", "control_ids": ["COMP-003"], "basis": "self_reported"},
            {"key": "inquiry_owner", "description": "A designated owner exists for regulator/third-party inquiries.", "control_ids": ["COMP-006"], "basis": "self_reported"},
            {"key": "data_flow_records", "description": "Data-flow/processing records are documented for critical systems.", "control_ids": ["COMP-007"], "basis": "self_reported"},
            {"key": "workforce_training", "description": "Sector data-handling training is included in the awareness program.", "control_ids": ["COMP-008"], "basis": "self_reported"},
            {"key": "change_review", "description": "An internal compliance checklist is reviewed before major IT changes.", "control_ids": ["COMP-009"], "basis": "self_reported"},
        ],
    },
    "Sector regulators (RBI / SEBI / NCIIPC, as applicable)": {
        "url": None,
        "requirements": [
            {"key": "periodic_sector_review", "description": "Sector-specific data handling obligations are reviewed periodically.", "control_ids": ["COMP-004"], "basis": "self_reported"},
        ],
    },
}


def _answers_by_control(assessment_id: str) -> dict[str, dict]:
    return {a["control_id"]: a for a in answers_repo.find({"assessment_id": assessment_id})}


def _all_controls_affirmative(control_ids: list[str], answers: dict[str, dict]) -> bool:
    if not control_ids:
        return False
    return all(answers.get(cid, {}).get("score", 0) > 0 for cid in control_ids)


def _log_retention_meets_requirement(assessment_id: str) -> bool:
    sources = log_sources_repo.find({"assessment_id": assessment_id})
    return any(s.get("enabled") and s.get("retention_days", 0) >= CERT_IN_LOG_RETENTION_DAYS for s in sources)


def _ntp_probe_result(assessment_id: str) -> bool | None:
    """Returns the real probe result for CHECK_006 if one exists, else None
    (meaning: fall back to the self-reported answer instead)."""
    runs = probe_runs_repo.find({"assessment_id": assessment_id, "verification_status": "verified"})
    for run in runs:
        checks = probe_checks_repo.find({"probe_run_id": run["id"], "check_id": "CHECK_006"})
        if checks:
            return bool(checks[0].get("result"))
    return None


def compute_compliance(organisation_id: str, assessment_id: str) -> RegulatoryComplianceOut:
    answers = _answers_by_control(assessment_id)

    frameworks_out: list[FrameworkComplianceOut] = []
    for framework_name, framework_def in FRAMEWORKS.items():
        requirements_out: list[RequirementOut] = []
        for req in framework_def["requirements"]:
            if req["key"] == "log_retention_180d":
                met = _log_retention_meets_requirement(assessment_id)
            elif req["key"] == "ntp_sync":
                probe_result = _ntp_probe_result(assessment_id)
                met = probe_result if probe_result is not None else _all_controls_affirmative(req["control_ids"], answers)
            else:
                met = _all_controls_affirmative(req["control_ids"], answers)

            requirements_out.append(
                RequirementOut(
                    key=req["key"],
                    description=req["description"],
                    met=met,
                    basis=req["basis"],
                    control_ids=req["control_ids"],
                )
            )

        verdict = "compliant" if all(r.met for r in requirements_out) else "non_compliant"
        frameworks_out.append(
            FrameworkComplianceOut(
                framework=framework_name,
                verdict=verdict,
                url=framework_def["url"],
                requirements=requirements_out,
            )
        )

    return RegulatoryComplianceOut(
        assessment_id=assessment_id,
        organisation_id=organisation_id,
        frameworks=frameworks_out,
        disclaimer=DISCLAIMER,
    )
