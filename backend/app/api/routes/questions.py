from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, get_current_user
from app.models.question import QuestionOut
from app.services import routing_service

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("", response_model=list[QuestionOut])
def list_questions(
    sector: str,
    role: str,
    language: str = "en",
    mode: str = "full",
    user: CurrentUser = Depends(get_current_user),
):
    return routing_service.get_routed_questions(sector, role, language, mode)
