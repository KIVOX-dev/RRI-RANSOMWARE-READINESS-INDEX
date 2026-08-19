from typing import Optional

from pydantic import BaseModel


class RequirementOut(BaseModel):
    key: str
    description: str
    met: bool
    basis: str
    control_ids: list[str]


class FrameworkComplianceOut(BaseModel):
    framework: str
    verdict: str
    url: Optional[str] = None
    requirements: list[RequirementOut]


class RegulatoryComplianceOut(BaseModel):
    assessment_id: str
    organisation_id: str
    frameworks: list[FrameworkComplianceOut]
    disclaimer: str
