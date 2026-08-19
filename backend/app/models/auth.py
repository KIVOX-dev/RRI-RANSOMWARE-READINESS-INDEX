from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.common import Language, UserRole


class OrganisationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    sector: str
    size: Optional[str] = None
    location: Optional[str] = None
    parent_organisation_id: Optional[str] = None


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    organisation: OrganisationCreate
    language: Language = Language.en


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: str
    role: UserRole
    organisation_id: str
    language: Language
    status: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
