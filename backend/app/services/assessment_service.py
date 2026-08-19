from fastapi import HTTPException, status

from app.models.assessment import AnswerSubmitRequest, AssessmentStartRequest
from app.models.common import OrganisationVerificationStatus
from app.repositories.base import now_utc
from app.repositories.collections import answers_repo, assessments_repo, organisations_repo, questions_repo
from app.services import ledger_service, routing_service, scoring_service


def start_assessment(organisation_id: str, created_by: str, payload: AssessmentStartRequest) -> dict:
    # Assessments created before the "mode" field existed have no mode
    # stored at all; treat those as "full" (the prior, only behaviour) so
    # they're still found as resumable rather than orphaned by this field.
    mode_filter = {"$in": [payload.mode.value, None]} if payload.mode.value == "full" else payload.mode.value
    existing = assessments_repo.find(
        {
            "organisation_id": organisation_id,
            "sector": payload.sector.value,
            "role": payload.role.value,
            "mode": mode_filter,
            "status": {"$in": ["draft", "in_progress"]},
        },
        sort=[("started_at", -1)],
        limit=1,
    )
    if existing:
        return existing[0]

    total_controls = len(
        routing_service.get_routed_questions(payload.sector.value, payload.role.value, payload.language.value, payload.mode.value)
    )

    assessment_id = assessments_repo.insert(
        {
            "organisation_id": organisation_id,
            "created_by": created_by,
            "sector": payload.sector.value,
            "role": payload.role.value,
            "language": payload.language.value,
            "mode": payload.mode.value,
            "status": "in_progress",
            "progress": 0.0,
            "started_at": now_utc(),
            "completed_at": None,
            "maturity_score": None,
            "assurance_score": None,
            "domain_scores": [],
            "high_impact_gaps": [],
            "total_controls": total_controls,
            "answered_controls": 0,
        }
    )
    return assessments_repo.get_by_id(assessment_id)


def get_assessment(assessment_id: str) -> dict:
    assessment = assessments_repo.get_by_id(assessment_id)
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    return assessment


def list_assessments(organisation_id: str) -> list[dict]:
    return assessments_repo.find({"organisation_id": organisation_id}, sort=[("started_at", -1)])


def submit_answer(assessment_id: str, answered_by: str, payload: AnswerSubmitRequest) -> dict:
    assessment = get_assessment(assessment_id)
    if assessment["status"] == "completed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assessment already completed")

    question = questions_repo.find_one({"control_id": payload.control_id, "active": True})
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown control_id")

    score = routing_service.score_answer(question, payload.answer)

    existing = answers_repo.find_one({"assessment_id": assessment_id, "control_id": payload.control_id})
    doc = {
        "assessment_id": assessment_id,
        "question_id": question["id"],
        "control_id": payload.control_id,
        "answer": payload.answer,
        "score": score,
        "weight": question["weight"],
        "impact_level": question["impact_level"],
        "answered_by": answered_by,
        "answered_at": now_utc(),
    }
    if existing:
        answers_repo.update_by_id(existing["id"], doc)
        answer_id = existing["id"]
    else:
        answer_id = answers_repo.insert(doc)

    if assessment["status"] == "draft":
        assessments_repo.update_by_id(assessment_id, {"status": "in_progress"})

    scoring_service.recompute_assessment_scores(assessment_id)
    return answers_repo.get_by_id(answer_id)


def list_answers(assessment_id: str) -> list[dict]:
    return answers_repo.find({"assessment_id": assessment_id})


def complete_assessment(assessment_id: str) -> dict:
    assessment = get_assessment(assessment_id)
    if assessment["status"] == "completed":
        return assessment

    org = organisations_repo.get_by_id(assessment["organisation_id"])
    if org and org.get("parent_organisation_id") and org.get("verification_status") != OrganisationVerificationStatus.verified.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This organisation is a sub-organisation pending verification by its parent organisation and cannot complete an assessment yet.",
        )

    scoring_service.recompute_assessment_scores(assessment_id)
    assessment = get_assessment(assessment_id)

    assessments_repo.update_by_id(assessment_id, {"status": "completed", "completed_at": now_utc()})
    assessment = get_assessment(assessment_id)

    ledger_payload = {
        "assessment_id": assessment_id,
        "organisation_id": assessment["organisation_id"],
        "maturity_score": assessment["maturity_score"],
        "assurance_score": assessment["assurance_score"],
        "completed_at": str(assessment.get("completed_at")),
    }
    ledger_service.create_ledger_entry(assessment["organisation_id"], ledger_payload, assessment_id=assessment_id)

    return get_assessment(assessment_id)
