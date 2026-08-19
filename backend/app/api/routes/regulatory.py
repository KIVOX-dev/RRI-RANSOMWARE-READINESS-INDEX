from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, assert_org_access, get_current_user
from app.models.regulatory import RegulatoryComplianceOut
from app.services import assessment_service, regulatory_compliance_service

router = APIRouter(prefix="/regulatory", tags=["regulatory"])


@router.get("/{assessment_id}/compliance", response_model=RegulatoryComplianceOut)
def get_compliance(assessment_id: str, user: CurrentUser = Depends(get_current_user)):
    assessment = assessment_service.get_assessment(assessment_id)
    assert_org_access(user, assessment["organisation_id"])
    return regulatory_compliance_service.compute_compliance(assessment["organisation_id"], assessment_id)
