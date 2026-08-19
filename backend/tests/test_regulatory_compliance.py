from app.repositories.collections import (
    answers_repo,
    assessments_repo,
    log_sources_repo,
    organisations_repo,
    probe_checks_repo,
    probe_runs_repo,
    users_repo,
)
from app.services import regulatory_compliance_service

ALL_CONTROL_IDS = [
    "COMP-001", "COMP-002", "COMP-003", "COMP-004", "COMP-006", "COMP-007",
    "COMP-008", "COMP-009", "COMP-010", "IR-006", "IR-011", "PROBE-NTP-SYNC",
]


def _make_org_and_assessment():
    org_id = organisations_repo.insert({"name": "Compliance Org", "sector": "generic", "is_synthetic": False})
    user_id = users_repo.insert(
        {"organisation_id": org_id, "name": "T", "email": "c@c.com", "password_hash": "x", "role": "org_admin", "language": "en", "status": "active"}
    )
    assessment_id = assessments_repo.insert(
        {
            "organisation_id": org_id, "created_by": user_id, "sector": "generic", "role": "it_administrator",
            "language": "en", "status": "in_progress", "progress": 0, "total_controls": 0, "answered_controls": 0,
            "domain_scores": [], "high_impact_gaps": [],
        }
    )
    return org_id, assessment_id, user_id


def _answer(assessment_id, user_id, control_id, score):
    answers_repo.insert(
        {"assessment_id": assessment_id, "question_id": control_id, "control_id": control_id, "answer": score > 0, "score": score, "weight": 1.0, "impact_level": "medium", "answered_by": user_id}
    )


def test_no_answers_means_every_framework_non_compliant():
    org_id, assessment_id, _ = _make_org_and_assessment()

    result = regulatory_compliance_service.compute_compliance(org_id, assessment_id)

    assert len(result.frameworks) == 3
    for framework in result.frameworks:
        assert framework.verdict == "non_compliant"
        assert all(not r.met for r in framework.requirements)


def test_fully_answered_org_with_adequate_log_retention_is_compliant_everywhere():
    org_id, assessment_id, user_id = _make_org_and_assessment()
    for control_id in ALL_CONTROL_IDS:
        _answer(assessment_id, user_id, control_id, 5.0)
    log_sources_repo.insert({"assessment_id": assessment_id, "source_name": "SIEM", "enabled": True, "retention_days": 200, "monitored": True, "covered_stages": [], "gaps": []})

    result = regulatory_compliance_service.compute_compliance(org_id, assessment_id)

    by_name = {f.framework: f for f in result.frameworks}
    assert by_name["CERT-In Directions, 2022"].verdict == "compliant"
    assert by_name["DPDP Act, 2023"].verdict == "compliant"
    assert by_name["Sector regulators (RBI / SEBI / NCIIPC, as applicable)"].verdict == "compliant"


def test_log_retention_below_180_days_fails_cert_in_even_if_log_006_style_answers_are_affirmative():
    org_id, assessment_id, user_id = _make_org_and_assessment()
    for control_id in ALL_CONTROL_IDS:
        _answer(assessment_id, user_id, control_id, 5.0)
    # Only meets the assessment's own weaker 90-day bar, not CERT-In's real 180-day one.
    log_sources_repo.insert({"assessment_id": assessment_id, "source_name": "SIEM", "enabled": True, "retention_days": 90, "monitored": True, "covered_stages": [], "gaps": []})

    result = regulatory_compliance_service.compute_compliance(org_id, assessment_id)

    cert_in = next(f for f in result.frameworks if f.framework == "CERT-In Directions, 2022")
    assert cert_in.verdict == "non_compliant"
    retention_req = next(r for r in cert_in.requirements if r.key == "log_retention_180d")
    assert retention_req.met is False


def test_ntp_probe_result_overrides_self_reported_answer():
    org_id, assessment_id, user_id = _make_org_and_assessment()
    for control_id in ALL_CONTROL_IDS:
        _answer(assessment_id, user_id, control_id, 5.0)
    log_sources_repo.insert({"assessment_id": assessment_id, "source_name": "SIEM", "enabled": True, "retention_days": 200, "monitored": True, "covered_stages": [], "gaps": []})

    # Self-report says yes, but the real signed probe result says NTP sync failed.
    run_id = probe_runs_repo.insert({"assessment_id": assessment_id, "organisation_id": org_id, "verification_status": "verified"})
    probe_checks_repo.insert({"probe_run_id": run_id, "check_id": "CHECK_006", "result": False, "control_id": "PROBE-NTP-SYNC"})

    result = regulatory_compliance_service.compute_compliance(org_id, assessment_id)

    cert_in = next(f for f in result.frameworks if f.framework == "CERT-In Directions, 2022")
    assert cert_in.verdict == "non_compliant"
    ntp_req = next(r for r in cert_in.requirements if r.key == "ntp_sync")
    assert ntp_req.met is False


def test_flipping_one_control_only_affects_its_own_framework():
    org_id, assessment_id, user_id = _make_org_and_assessment()
    for control_id in ALL_CONTROL_IDS:
        _answer(assessment_id, user_id, control_id, 5.0)
    log_sources_repo.insert({"assessment_id": assessment_id, "source_name": "SIEM", "enabled": True, "retention_days": 200, "monitored": True, "covered_stages": [], "gaps": []})

    # COMP-001 only backs a DPDP requirement, not CERT-In or Sector regulators.
    answers_repo.collection.update_one({"assessment_id": assessment_id, "control_id": "COMP-001"}, {"$set": {"score": 0.0}})

    result = regulatory_compliance_service.compute_compliance(org_id, assessment_id)
    by_name = {f.framework: f for f in result.frameworks}

    assert by_name["DPDP Act, 2023"].verdict == "non_compliant"
    assert by_name["CERT-In Directions, 2022"].verdict == "compliant"
    assert by_name["Sector regulators (RBI / SEBI / NCIIPC, as applicable)"].verdict == "compliant"
