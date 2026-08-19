from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_access_token
from app.models.common import UserRole
from app.repositories.collections import audit_logs_repo
from app.repositories.base import now_utc

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class CurrentUser:
    id: str
    email: str
    name: str
    role: UserRole
    organisation_id: str


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> CurrentUser:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    return CurrentUser(
        id=payload["sub"],
        email=payload.get("email", ""),
        name=payload.get("name", ""),
        role=UserRole(payload.get("role", UserRole.org_user.value)),
        organisation_id=payload.get("organisation_id", ""),
    )


def require_roles(*roles: UserRole):
    def _dependency(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return _dependency


def require_platform_admin(request: Request, user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if user.role != UserRole.platform_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Platform admin access required")
    audit_logs_repo.insert(
        {
            "user_id": user.id,
            "organisation_id": user.organisation_id,
            "action": "platform_admin_access",
            "resource_type": "route",
            "resource_id": str(request.url.path),
            "metadata": {"method": request.method},
            "ip_address": request.client.host if request.client else None,
            "timestamp": now_utc(),
        }
    )
    return user


def assert_org_access(user: CurrentUser, organisation_id: str) -> None:
    if user.role == UserRole.platform_admin:
        return
    if user.organisation_id != organisation_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cross-organisation access denied")
