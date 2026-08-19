from fastapi import HTTPException, status

from app.core.security import create_access_token, hash_password, verify_password
from app.models.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut
from app.models.common import OrganisationVerificationStatus, UserRole
from app.repositories.base import now_utc
from app.repositories.collections import organisations_repo, users_repo
from app.services import ledger_service


def _issue_token(user: dict) -> TokenResponse:
    token = create_access_token(
        subject=user["id"],
        claims={
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "organisation_id": user["organisation_id"],
        },
    )
    return TokenResponse(access_token=token, user=UserOut(**user))


def register(payload: RegisterRequest) -> TokenResponse:
    if users_repo.find_one({"email": payload.email.lower()}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    parent_organisation_id = payload.organisation.parent_organisation_id
    parent_org = None
    if parent_organisation_id:
        parent_org = organisations_repo.get_by_id(parent_organisation_id)
        if not parent_org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent organisation not found")

    org_id = organisations_repo.insert(
        {
            "name": payload.organisation.name,
            "sector": payload.organisation.sector,
            "size": payload.organisation.size,
            "location": payload.organisation.location,
            "is_synthetic": False,
            "parent_organisation_id": parent_organisation_id,
            "verification_status": (
                OrganisationVerificationStatus.pending.value if parent_org else OrganisationVerificationStatus.verified.value
            ),
        }
    )

    if parent_org:
        # The "message sent to the main organisation's ledger" — a
        # tamper-evident record, in the parent's own chain, that this
        # sub-org registration happened. The parent approves it by clicking
        # their Ledger page's existing Verify button (see
        # ledger_service.verify_chain_and_process_approvals).
        ledger_service.create_ledger_entry(
            parent_organisation_id,
            {
                "type": "sub_organisation_request",
                "sub_organisation_id": org_id,
                "sub_organisation_name": payload.organisation.name,
            },
            record_type="sub_organisation_request",
            sub_organisation_id=org_id,
        )

    user_id = users_repo.insert(
        {
            "organisation_id": org_id,
            "name": payload.name,
            "email": payload.email.lower(),
            "password_hash": hash_password(payload.password),
            "role": UserRole.org_admin.value,
            "language": payload.language.value,
            "status": "active",
        }
    )
    user = users_repo.get_by_id(user_id)
    return _issue_token(user)


def login(payload: LoginRequest) -> TokenResponse:
    user = users_repo.find_one({"email": payload.email.lower()})
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if user.get("status") != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is not active")
    users_repo.update_by_id(user["id"], {"last_login_at": now_utc()})
    return _issue_token(user)
