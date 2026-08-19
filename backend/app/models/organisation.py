from typing import Optional

from pydantic import BaseModel

from app.models.common import OrganisationVerificationStatus


class OrganisationOut(BaseModel):
    id: str
    name: str
    sector: str
    size: Optional[str] = None
    location: Optional[str] = None
    is_synthetic: bool = False
    parent_organisation_id: Optional[str] = None
    verification_status: OrganisationVerificationStatus = OrganisationVerificationStatus.verified


class OrganisationDirectoryEntry(BaseModel):
    id: str
    name: str
