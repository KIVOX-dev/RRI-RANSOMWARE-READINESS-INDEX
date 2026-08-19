from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, assert_org_access, get_current_user
from app.models.detection import DetectionStageOut, DwellTimeReadinessOut
from app.services import assessment_service, attck_service, cis_cdm_service, detection_service, dwell_time_service

router = APIRouter(prefix="/detection", tags=["detection"])


@router.get("/{assessment_id}/matrix", response_model=list[DetectionStageOut])
def get_matrix(assessment_id: str, user: CurrentUser = Depends(get_current_user)):
    assessment = assessment_service.get_assessment(assessment_id)
    assert_org_access(user, assessment["organisation_id"])
    return detection_service.compute_detection_matrix(assessment_id)


@router.get("/attck-reference")
def get_attck_reference(user: CurrentUser = Depends(get_current_user)):
    """Full curated MITRE ATT&CK CTI reference set (not org-scoped — this is
    static public threat-intel data, the same for every organisation)."""
    return {"meta": attck_service.get_meta(), "techniques": list(attck_service.get_all_techniques().values())}


@router.get("/cis-cdm-reference")
def get_cis_cdm_reference(user: CurrentUser = Depends(get_current_user)):
    """CIS Community Defense Model v2.0's published ransomware-pattern
    coverage data (not org-scoped — static, external benchmark data)."""
    return cis_cdm_service.get_full_reference()


@router.get("/{assessment_id}/dwell-time", response_model=DwellTimeReadinessOut)
def get_dwell_time(assessment_id: str, user: CurrentUser = Depends(get_current_user)):
    assessment = assessment_service.get_assessment(assessment_id)
    assert_org_access(user, assessment["organisation_id"])
    return dwell_time_service.compute_dwell_time_readiness(assessment_id)
