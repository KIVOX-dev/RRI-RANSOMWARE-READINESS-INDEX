from app.repositories.collections import (
    answers_repo,
    assessments_repo,
    evidence_repo,
    organisations_repo,
    questions_repo,
    scoring_configs_repo,
    users_repo,
)
from app.services import scoring_service


def _seed_minimal_scoring_config():
    scoring_configs_repo.insert(
        {
            "version": 1,
            "domains": ["Test Domain"],
            "impact_multipliers": {"low": 1.0, "medium": 1.5, "high": 2.0},
            "assurance_rules": {
                "unverified_claim_weight": 0.35,
                "evidence_weight": 0.75,
                "evidence_verified_weight": 0.9,
                "probe_verified_weight": 1.0,
                "high_impact_assurance_threshold": 0.6,
            },
            "active": True,
        }
    )


def _seed_question(control_id, domain, impact, weight):
    return questions_repo.insert(
        {
            "control_id": control_id,
            "title": {"en": control_id},
            "domain": domain,
            "sector": "generic",
            "roles": ["it_administrator"],
            "answer_type": "boolean",
            "options": [],
            "weight": weight,
            "impact_level": impact,
            "evidence_required": False,
            "active": True,
        }
    )


def _make_org_and_assessment():
    org_id = organisations_repo.insert({"name": "Test Org", "sector": "generic", "is_synthetic": False})
    user_id = users_repo.insert({"organisation_id": org_id, "name": "T", "email": "t@t.com", "password_hash": "x", "role": "org_admin", "language": "en", "status": "active"})
    assessment_id = assessments_repo.insert(
        {
            "organisation_id": org_id,
            "created_by": user_id,
            "sector": "generic",
            "role": "it_administrator",
            "language": "en",
            "status": "in_progress",
            "progress": 0,
            "total_controls": 2,
            "answered_controls": 0,
            "domain_scores": [],
            "high_impact_gaps": [],
        }
    )
    return org_id, user_id, assessment_id


def test_maturity_score_is_weighted_average_of_answers():
    _seed_minimal_scoring_config()
    _seed_question("C-HIGH", "Test Domain", "high", weight=2.0)
    _seed_question("C-LOW", "Test Domain", "low", weight=1.0)
    org_id, user_id, assessment_id = _make_org_and_assessment()

    # C-HIGH answered "yes" (score 5.0), C-LOW answered "no" (score 0.0)
    answers_repo.insert({"assessment_id": assessment_id, "question_id": "q1", "control_id": "C-HIGH", "answer": True, "score": 5.0, "weight": 2.0, "impact_level": "high", "answered_by": user_id})
    answers_repo.insert({"assessment_id": assessment_id, "question_id": "q2", "control_id": "C-LOW", "answer": False, "score": 0.0, "weight": 1.0, "impact_level": "low", "answered_by": user_id})

    result = scoring_service.recompute_assessment_scores(assessment_id)

    # effective weights: high=2.0*2.0=4.0, low=1.0*1.0=1.0 -> weighted avg = (5*4 + 0*1)/5 = 4.0
    assert result["maturity_score"] == 4.0


def test_unverified_high_impact_claim_is_flagged_as_gap():
    _seed_minimal_scoring_config()
    _seed_question("C-CRITICAL", "Test Domain", "high", weight=3.0)
    org_id, user_id, assessment_id = _make_org_and_assessment()

    # Claimed fully implemented but with zero evidence and no probe verification
    answers_repo.insert({"assessment_id": assessment_id, "question_id": "q1", "control_id": "C-CRITICAL", "answer": True, "score": 5.0, "weight": 3.0, "impact_level": "high", "answered_by": user_id})

    result = scoring_service.recompute_assessment_scores(assessment_id)

    assert result["assurance_score"] < 60.0  # only the "unverified claim" fraction (0.35) applies
    gap_controls = [g["control_id"] for g in result["high_impact_gaps"]]
    assert "C-CRITICAL" in gap_controls


def test_evidence_upload_raises_assurance_and_clears_gap():
    _seed_minimal_scoring_config()
    _seed_question("C-CRITICAL", "Test Domain", "high", weight=3.0)
    org_id, user_id, assessment_id = _make_org_and_assessment()
    answers_repo.insert({"assessment_id": assessment_id, "question_id": "q1", "control_id": "C-CRITICAL", "answer": True, "score": 5.0, "weight": 3.0, "impact_level": "high", "answered_by": user_id})

    before = scoring_service.recompute_assessment_scores(assessment_id)
    assert len(before["high_impact_gaps"]) == 1

    evidence_repo.insert(
        {
            "assessment_id": assessment_id,
            "organisation_id": org_id,
            "control_id": "C-CRITICAL",
            "filename": "policy.pdf",
            "object_key": "x/y/z.pdf",
            "mime_type": "application/pdf",
            "size": 1234,
            "checksum": "abc",
            "uploaded_by": user_id,
            "verification_status": "verified",
        }
    )

    after = scoring_service.recompute_assessment_scores(assessment_id)
    assert after["assurance_score"] > before["assurance_score"]
    assert len(after["high_impact_gaps"]) == 0
