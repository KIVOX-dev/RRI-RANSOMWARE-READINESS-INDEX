from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, get_current_user
from app.services.scoring_service import get_active_scoring_config

router = APIRouter(prefix="/scoring", tags=["scoring"])


@router.get("/config")
def get_config(user: CurrentUser = Depends(get_current_user)):
    """Read-only view of the active scoring configuration — weights and
    assurance rules are stored in the database, never hardcoded."""
    return get_active_scoring_config()
