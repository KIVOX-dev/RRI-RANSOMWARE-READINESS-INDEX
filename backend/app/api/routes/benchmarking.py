from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, assert_org_access, get_current_user
from app.models.benchmarking import BenchmarkOut, TrendOut
from app.services import benchmarking_service, trends_service

router = APIRouter(tags=["benchmarking"])


@router.get("/benchmarking/{organisation_id}", response_model=BenchmarkOut)
def get_benchmark(organisation_id: str, user: CurrentUser = Depends(get_current_user)):
    assert_org_access(user, organisation_id)
    return benchmarking_service.get_benchmark(organisation_id)


@router.get("/trends/{organisation_id}", response_model=TrendOut)
def get_trends(organisation_id: str, user: CurrentUser = Depends(get_current_user)):
    assert_org_access(user, organisation_id)
    return trends_service.get_trends(organisation_id)
