from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.deps import CurrentUser, assert_org_access, get_current_user, require_platform_admin
from app.models.evidence import EvidenceOut
from app.repositories.collections import evidence_repo
from app.services import assessment_service, evidence_service

router = APIRouter(prefix="/evidence", tags=["evidence"])


def _get_evidence_or_404(evidence_id: str) -> dict:
    evidence = evidence_repo.get_by_id(evidence_id)
    if not evidence:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found")
    return evidence


# Registered before the "/{assessment_id}/{control_id}" upload route below —
# both are two-segment POST paths, and FastAPI/Starlette matches path
# templates in registration order, so a literal ".../{id}/verify" route
# declared after a same-shaped "{x}/{y}" route would otherwise never be
# reached (confirmed live: it 422'd on the upload route's required `file`
# field instead of running this one).
@router.post("/{evidence_id}/verify", response_model=EvidenceOut)
def verify_evidence(evidence_id: str, user: CurrentUser = Depends(require_platform_admin)):
    """Independent review, by design: verification is only meaningful if
    it's not the same org self-attesting its own evidence, so this is
    platform-admin-only, same as the Ledger's Demo Tamper and the
    Regulator Console."""
    _get_evidence_or_404(evidence_id)
    return evidence_service.set_verification_status(evidence_id, "verified")


@router.post("/{evidence_id}/reject", response_model=EvidenceOut)
def reject_evidence(evidence_id: str, user: CurrentUser = Depends(require_platform_admin)):
    _get_evidence_or_404(evidence_id)
    return evidence_service.set_verification_status(evidence_id, "rejected")


@router.post("/{assessment_id}/{control_id}", response_model=EvidenceOut)
def upload_evidence(
    assessment_id: str,
    control_id: str,
    file: UploadFile = File(...),
    user: CurrentUser = Depends(get_current_user),
):
    assessment = assessment_service.get_assessment(assessment_id)
    assert_org_access(user, assessment["organisation_id"])
    return evidence_service.upload_evidence(assessment_id, assessment["organisation_id"], control_id, user.id, file)


@router.get("/{assessment_id}", response_model=list[EvidenceOut])
def list_evidence(assessment_id: str, user: CurrentUser = Depends(get_current_user)):
    assessment = assessment_service.get_assessment(assessment_id)
    assert_org_access(user, assessment["organisation_id"])
    return evidence_service.list_evidence(assessment_id)


@router.delete("/{evidence_id}")
def delete_evidence(evidence_id: str, user: CurrentUser = Depends(get_current_user)):
    evidence = _get_evidence_or_404(evidence_id)
    assert_org_access(user, evidence["organisation_id"])
    evidence_service.delete_evidence(evidence_id)
    return {"status": "deleted"}
