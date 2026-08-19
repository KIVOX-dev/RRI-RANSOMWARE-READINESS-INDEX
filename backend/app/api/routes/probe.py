from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from app.api.deps import CurrentUser, assert_org_access, get_current_user
from app.core.config import get_settings
from app.models.probe import ProbeIngestRequest, ProbeRunOut
from app.services import assessment_service, probe_service

router = APIRouter(prefix="/probe", tags=["probe"])


@router.post("/ingest", response_model=ProbeRunOut)
def ingest(payload: ProbeIngestRequest, user: CurrentUser = Depends(get_current_user)):
    assessment = assessment_service.get_assessment(payload.assessment_id)
    assert_org_access(user, assessment["organisation_id"])
    return probe_service.ingest_probe_result(payload)


@router.get("/runs/{assessment_id}", response_model=list[ProbeRunOut])
def list_runs(assessment_id: str, user: CurrentUser = Depends(get_current_user)):
    assessment = assessment_service.get_assessment(assessment_id)
    assert_org_access(user, assessment["organisation_id"])
    return probe_service.list_probe_runs(assessment_id)


@router.get("/public-key")
def public_key(user: CurrentUser = Depends(get_current_user)):
    return {"public_key_b64": probe_service.get_probe_public_key_b64()}


@router.get("/download/powershell", response_class=PlainTextResponse)
def download_powershell(user: CurrentUser = Depends(get_current_user)):
    return probe_service.render_powershell_script(get_settings().public_backend_url)


@router.get("/download/bash", response_class=PlainTextResponse)
def download_bash(user: CurrentUser = Depends(get_current_user)):
    return probe_service.render_bash_script(get_settings().public_backend_url)
