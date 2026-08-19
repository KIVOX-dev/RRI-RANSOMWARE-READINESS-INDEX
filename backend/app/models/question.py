from typing import Optional

from pydantic import BaseModel

from app.models.common import AnswerType, ImpactLevel


class QuestionOption(BaseModel):
    value: str
    label: str
    score: float


class MicroLearning(BaseModel):
    why_it_matters: str
    risk_addressed: str
    good_practice: str
    evidence_hint: str


class RegulatoryReference(BaseModel):
    framework: str
    note: str
    url: Optional[str] = None


class RegulatoryContext(BaseModel):
    references: list[RegulatoryReference] = []
    disclaimer: str = (
        "Informational awareness only, not legal advice. Confirm current obligations with your "
        "organisation's legal/compliance counsel before relying on this for a compliance decision."
    )


class CisCdmSafeguard(BaseModel):
    id: str
    title: str
    ig: str
    technique_count: Optional[int] = None


class CisCdmReference(BaseModel):
    safeguards: list[CisCdmSafeguard] = []
    note: str
    source_title: str = "CIS Community Defense Model v2.0"
    source_url: str = "https://www.cisecurity.org/insights/blog/cis-introduces-v2-0-of-the-cis-community-defense-model"


class QuestionOut(BaseModel):
    id: str
    control_id: str
    domain: str
    title: str
    description: str
    answer_type: AnswerType
    options: list[QuestionOption] = []
    impact_level: ImpactLevel
    weight: float
    evidence_required: bool
    micro_learning: Optional[MicroLearning] = None
    regulatory_context: Optional[RegulatoryContext] = None
    cis_cdm_reference: Optional[CisCdmReference] = None
    basic_track: bool = False
    order: int = 0
    round: int = 1
    round_count: int = 1
