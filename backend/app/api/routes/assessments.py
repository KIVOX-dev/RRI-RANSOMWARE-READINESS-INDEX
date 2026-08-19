from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, assert_org_access, get_current_user
from app.models.assessment import AnswerSubmitRequest, AssessmentOut, AssessmentStartRequest
from app.services import assessment_service

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.post("/start", response_model=AssessmentOut)
def start_assessment(payload: AssessmentStartRequest, user: CurrentUser = Depends(get_current_user)):
    return assessment_service.start_assessment(user.organisation_id, user.id, payload)


@router.get("", response_model=list[AssessmentOut])
def list_assessments(user: CurrentUser = Depends(get_current_user)):
    return assessment_service.list_assessments(user.organisation_id)


@router.get("/{assessment_id}", response_model=AssessmentOut)
def get_assessment(assessment_id: str, user: CurrentUser = Depends(get_current_user)):
    assessment = assessment_service.get_assessment(assessment_id)
    assert_org_access(user, assessment["organisation_id"])
    return assessment


@router.get("/{assessment_id}/resume", response_model=AssessmentOut)
def resume_assessment(assessment_id: str, user: CurrentUser = Depends(get_current_user)):
    assessment = assessment_service.get_assessment(assessment_id)
    assert_org_access(user, assessment["organisation_id"])
    return assessment


@router.post("/{assessment_id}/answers")
def submit_answer(assessment_id: str, payload: AnswerSubmitRequest, user: CurrentUser = Depends(get_current_user)):
    assessment = assessment_service.get_assessment(assessment_id)
    assert_org_access(user, assessment["organisation_id"])
    return assessment_service.submit_answer(assessment_id, user.id, payload)


@router.get("/{assessment_id}/answers")
def list_answers(assessment_id: str, user: CurrentUser = Depends(get_current_user)):
    assessment = assessment_service.get_assessment(assessment_id)
    assert_org_access(user, assessment["organisation_id"])
    return assessment_service.list_answers(assessment_id)


@router.post("/{assessment_id}/complete", response_model=AssessmentOut)
def complete_assessment(assessment_id: str, user: CurrentUser = Depends(get_current_user)):
    assessment = assessment_service.get_assessment(assessment_id)
    assert_org_access(user, assessment["organisation_id"])
    return assessment_service.complete_assessment(assessment_id)
