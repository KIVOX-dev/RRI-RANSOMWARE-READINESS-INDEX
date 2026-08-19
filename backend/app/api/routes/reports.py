from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, assert_org_access, get_current_user
from app.models.report import ReportGenerateRequest, ReportOut
from app.services import assessment_service, report_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/{assessment_id}/generate", response_model=ReportOut)
def generate(assessment_id: str, payload: ReportGenerateRequest, user: CurrentUser = Depends(get_current_user)):
    assessment = assessment_service.get_assessment(assessment_id)
    assert_org_access(user, assessment["organisation_id"])
    return report_service.generate_report(assessment_id, payload.report_type)


@router.get("/{assessment_id}", response_model=list[ReportOut])
def list_reports(assessment_id: str, user: CurrentUser = Depends(get_current_user)):
    assessment = assessment_service.get_assessment(assessment_id)
    assert_org_access(user, assessment["organisation_id"])
    return report_service.list_reports(assessment_id)


@router.get("/detail/{report_id}", response_model=ReportOut)
def get_report(report_id: str, user: CurrentUser = Depends(get_current_user)):
    return report_service.get_report(report_id)
