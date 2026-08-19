from app.repositories.collections import assessments_repo, evidence_repo, organisations_repo, users_repo
from app.services import evidence_service


def _make_assessment():
    org_id = organisations_repo.insert({"name": "Evidence Org", "sector": "generic", "is_synthetic": False})
    user_id = users_repo.insert(
        {"organisation_id": org_id, "name": "E", "email": "e@e.com", "password_hash": "x", "role": "org_admin", "language": "en", "status": "active"}
    )
    assessment_id = assessments_repo.insert(
        {
            "organisation_id": org_id, "created_by": user_id, "sector": "generic", "role": "it_administrator",
            "language": "en", "status": "in_progress", "progress": 0, "total_controls": 0, "answered_controls": 0,
            "domain_scores": [], "high_impact_gaps": [],
        }
    )
    return org_id, assessment_id, user_id


def test_uploaded_evidence_starts_pending():
    org_id, assessment_id, user_id = _make_assessment()
    evidence_id = evidence_repo.insert(
        {"assessment_id": assessment_id, "organisation_id": org_id, "control_id": "GOV-001", "filename": "f.pdf",
         "object_key": "k", "mime_type": "application/pdf", "size": 10, "checksum": "abc", "uploaded_by": user_id,
         "verification_status": "pending"}
    )
    assert evidence_repo.get_by_id(evidence_id)["verification_status"] == "pending"


def test_set_verification_status_can_verify_and_reject():
    org_id, assessment_id, user_id = _make_assessment()
    evidence_id = evidence_repo.insert(
        {"assessment_id": assessment_id, "organisation_id": org_id, "control_id": "GOV-001", "filename": "f.pdf",
         "object_key": "k", "mime_type": "application/pdf", "size": 10, "checksum": "abc", "uploaded_by": user_id,
         "verification_status": "pending"}
    )

    verified = evidence_service.set_verification_status(evidence_id, "verified")
    assert verified["verification_status"] == "verified"

    rejected = evidence_service.set_verification_status(evidence_id, "rejected")
    assert rejected["verification_status"] == "rejected"
