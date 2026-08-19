from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, assert_org_access, get_current_user
from app.models.remediation import RemediationItemOut
from app.services import assessment_service, remediation_service

router = APIRouter(prefix="/remediation", tags=["remediation"])


@router.post("/{assessment_id}/generate", response_model=list[RemediationItemOut])
def generate(assessment_id: str, user: CurrentUser = Depends(get_current_user)):
    assessment = assessment_service.get_assessment(assessment_id)
    assert_org_access(user, assessment["organisation_id"])
    return remediation_service.generate_remediation_items(assessment_id)


@router.get("/{assessment_id}", response_model=list[RemediationItemOut])
def list_items(
    assessment_id: str,
    domain: str | None = None,
    impact: str | None = None,
    effort: str | None = None,
    priority: str | None = None,
    user: CurrentUser = Depends(get_current_user),
):
    assessment = assessment_service.get_assessment(assessment_id)
    assert_org_access(user, assessment["organisation_id"])
    return remediation_service.list_remediation_items(assessment_id, domain, impact, effort, priority)
