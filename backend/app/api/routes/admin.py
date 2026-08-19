from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, require_platform_admin
from app.repositories.collections import assessments_repo, audit_logs_repo, organisations_repo

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/organisations")
def list_organisations(user: CurrentUser = Depends(require_platform_admin)):
    orgs = organisations_repo.find({})
    out = []
    for org in orgs:
        latest = assessments_repo.find({"organisation_id": org["id"]}, sort=[("started_at", -1)], limit=1)
        completed = assessments_repo.find({"organisation_id": org["id"], "status": "completed"}, sort=[("completed_at", -1)], limit=1)
        latest_probe_status = None
        out.append(
            {
                **org,
                "assessment_status": latest[0]["status"] if latest else "not_started",
                "maturity_score": completed[0]["maturity_score"] if completed else None,
                "assurance_score": completed[0]["assurance_score"] if completed else None,
                "completion_date": completed[0]["completed_at"] if completed else None,
                "total_assessments": assessments_repo.count({"organisation_id": org["id"]}),
            }
        )
    return out


@router.get("/audit-logs")
def list_audit_logs(user: CurrentUser = Depends(require_platform_admin), limit: int = 200):
    return audit_logs_repo.find({}, sort=[("timestamp", -1)], limit=limit)
