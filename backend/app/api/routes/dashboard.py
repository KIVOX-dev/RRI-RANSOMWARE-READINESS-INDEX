from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, assert_org_access, get_current_user
from app.services import assessment_service, dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/{assessment_id}")
def get_dashboard(assessment_id: str, user: CurrentUser = Depends(get_current_user)):
    assessment = assessment_service.get_assessment(assessment_id)
    assert_org_access(user, assessment["organisation_id"])
    return dashboard_service.get_dashboard(assessment_id)
