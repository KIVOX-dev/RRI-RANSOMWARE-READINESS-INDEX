from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, assert_org_access, get_current_user
from app.models.backup import BackupResilienceIn, BackupResilienceOut
from app.services import assessment_service, backup_service

router = APIRouter(prefix="/backup", tags=["backup"])


@router.put("/{assessment_id}", response_model=BackupResilienceOut)
def upsert(assessment_id: str, payload: BackupResilienceIn, user: CurrentUser = Depends(get_current_user)):
    assessment = assessment_service.get_assessment(assessment_id)
    assert_org_access(user, assessment["organisation_id"])
    return backup_service.upsert_backup_resilience(assessment_id, assessment["organisation_id"], payload)


@router.get("/{assessment_id}", response_model=BackupResilienceOut | None)
def get(assessment_id: str, user: CurrentUser = Depends(get_current_user)):
    assessment = assessment_service.get_assessment(assessment_id)
    assert_org_access(user, assessment["organisation_id"])
    return backup_service.get_backup_resilience(assessment_id)
