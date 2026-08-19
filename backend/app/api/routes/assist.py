from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import CurrentUser, get_current_user
from app.services import llm_assist_service

router = APIRouter(prefix="/assist", tags=["assist"])


class ExplainRequest(BaseModel):
    content: str


class ExplainResponse(BaseModel):
    available: bool
    explanation: str | None = None


@router.get("/available")
def available(user: CurrentUser = Depends(get_current_user)):
    return {"available": llm_assist_service.is_configured()}


@router.post("/explain", response_model=ExplainResponse)
def explain(payload: ExplainRequest, user: CurrentUser = Depends(get_current_user)):
    result = llm_assist_service.explain(payload.content)
    return ExplainResponse(available=result is not None, explanation=result)
