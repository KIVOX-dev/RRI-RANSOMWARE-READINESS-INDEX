from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import CurrentUser, assert_org_access, get_current_user
from app.models.organisation import OrganisationDirectoryEntry, OrganisationOut
from app.repositories.collections import organisations_repo

router = APIRouter(prefix="/organisations", tags=["organisations"])


@router.get("/directory", response_model=list[OrganisationDirectoryEntry])
def list_organisation_directory():
    """Unauthenticated on purpose — used to populate the 'parent
    organisation' picker during registration, before the new user has an
    account. Only top-level (non-sub) organisations are listed, and only
    their id/name — no other org details are exposed here."""
    orgs = organisations_repo.find({"parent_organisation_id": None}, sort=[("name", 1)])
    return [OrganisationDirectoryEntry(id=org["id"], name=org["name"]) for org in orgs]


@router.get("/me", response_model=OrganisationOut)
def get_my_organisation(user: CurrentUser = Depends(get_current_user)):
    org = organisations_repo.get_by_id(user.organisation_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organisation not found")
    return OrganisationOut(**org)


@router.get("/{organisation_id}", response_model=OrganisationOut)
def get_organisation(organisation_id: str, user: CurrentUser = Depends(get_current_user)):
    assert_org_access(user, organisation_id)
    org = organisations_repo.get_by_id(organisation_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organisation not found")
    return OrganisationOut(**org)
