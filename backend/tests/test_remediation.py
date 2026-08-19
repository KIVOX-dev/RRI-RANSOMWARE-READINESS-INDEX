from app.repositories.collections import answers_repo, assessments_repo, organisations_repo, questions_repo, users_repo
from app.services import remediation_service


def _seed_question(control_id, domain, impact, weight, good_practice="Do the thing."):
    return questions_repo.insert(
        {
            "control_id": control_id,
            "title": {"en": f"Title for {control_id}"},
            "domain": domain,
            "sector": "generic",
            "roles": ["it_administrator"],
            "answer_type": "boolean",
            "options": [],
            "weight": weight,
            "impact_level": impact,
            "evidence_required": False,
            "micro_learning": {"en": {"good_practice": good_practice}},
            "active": True,
        }
    )


def _make_assessment(high_impact_gap_controls=None):
    org_id = organisations_repo.insert({"name": "Remediation Org", "sector": "generic", "is_synthetic": False})
    user_id = users_repo.insert({"organisation_id": org_id, "name": "T", "email": "r@r.com", "password_hash": "x", "role": "org_admin", "language": "en", "status": "active"})
    assessment_id = assessments_repo.insert(
        {
            "organisation_id": org_id, "created_by": user_id, "sector": "generic", "role": "it_administrator",
            "language": "en", "status": "in_progress", "progress": 0, "total_controls": 0, "answered_controls": 0,
            "domain_scores": [],
            "high_impact_gaps": [{"control_id": c, "title": c, "domain": "d", "reason": "unverified"} for c in (high_impact_gap_controls or [])],
        }
    )
    return assessment_id, user_id


def test_fully_implemented_control_generates_no_remediation_item():
    _seed_question("C-GOOD", "Test Domain", "medium", weight=1.0)
    assessment_id, user_id = _make_assessment()
    answers_repo.insert({"assessment_id": assessment_id, "question_id": "q", "control_id": "C-GOOD", "answer": True, "score": 5.0, "weight": 1.0, "impact_level": "medium", "answered_by": user_id})

    items = remediation_service.generate_remediation_items(assessment_id)
    assert items == []


def test_unimplemented_high_impact_control_is_critical_priority():
    _seed_question("C-BAD", "Test Domain", "high", weight=2.0)
    assessment_id, user_id = _make_assessment()
    answers_repo.insert({"assessment_id": assessment_id, "question_id": "q", "control_id": "C-BAD", "answer": False, "score": 0.0, "weight": 2.0, "impact_level": "high", "answered_by": user_id})

    items = remediation_service.generate_remediation_items(assessment_id)
    assert len(items) == 1
    assert items[0]["priority"] == "critical"
    assert items[0]["control_id"] == "C-BAD"


def test_unverified_high_impact_gap_produces_remediation_item_even_if_scored_well():
    _seed_question("C-UNVERIFIED", "Test Domain", "high", weight=2.0)
    assessment_id, user_id = _make_assessment(high_impact_gap_controls=["C-UNVERIFIED"])
    answers_repo.insert({"assessment_id": assessment_id, "question_id": "q", "control_id": "C-UNVERIFIED", "answer": True, "score": 5.0, "weight": 2.0, "impact_level": "high", "answered_by": user_id})

    items = remediation_service.generate_remediation_items(assessment_id)
    assert len(items) == 1
    assert "evidenced or verified" in items[0]["issue"]


def test_items_are_sorted_by_priority_descending_severity():
    _seed_question("C-LOW-GAP", "Test Domain", "low", weight=1.0)
    _seed_question("C-CRITICAL-GAP", "Test Domain", "high", weight=2.0)
    assessment_id, user_id = _make_assessment()
    answers_repo.insert({"assessment_id": assessment_id, "question_id": "q1", "control_id": "C-LOW-GAP", "answer": False, "score": 2.5, "weight": 1.0, "impact_level": "low", "answered_by": user_id})
    answers_repo.insert({"assessment_id": assessment_id, "question_id": "q2", "control_id": "C-CRITICAL-GAP", "answer": False, "score": 0.0, "weight": 2.0, "impact_level": "high", "answered_by": user_id})

    items = remediation_service.generate_remediation_items(assessment_id)
    assert items[0]["control_id"] == "C-CRITICAL-GAP"
    assert items[0]["priority"] == "critical"
