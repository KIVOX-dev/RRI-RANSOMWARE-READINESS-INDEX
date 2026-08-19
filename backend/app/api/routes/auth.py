from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, get_current_user
from app.models.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut
from app.repositories.collections import users_repo
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest):
    return auth_service.register(payload)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    return auth_service.login(payload)


@router.get("/me", response_model=UserOut)
def me(user: CurrentUser = Depends(get_current_user)):
    doc = users_repo.get_by_id(user.id)
    return UserOut(**doc)


@router.post("/logout")
def logout(user: CurrentUser = Depends(get_current_user)):
    return {"status": "ok"}
