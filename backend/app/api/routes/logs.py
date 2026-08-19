from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, assert_org_access, get_current_user
from app.models.detection import LogGapAnalysisOut, LogSourceIn
from app.services import assessment_service, detection_service

router = APIRouter(prefix="/logs", tags=["logs"])


@router.put("/{assessment_id}/sources")
def upsert_sources(assessment_id: str, sources: list[LogSourceIn], user: CurrentUser = Depends(get_current_user)):
    assessment = assessment_service.get_assessment(assessment_id)
    assert_org_access(user, assessment["organisation_id"])
    return detection_service.upsert_log_sources(assessment_id, [s.model_dump() for s in sources])


@router.get("/{assessment_id}/gap-analysis", response_model=LogGapAnalysisOut)
def gap_analysis(assessment_id: str, user: CurrentUser = Depends(get_current_user)):
    assessment = assessment_service.get_assessment(assessment_id)
    assert_org_access(user, assessment["organisation_id"])
    return detection_service.get_log_gap_analysis(assessment_id)
