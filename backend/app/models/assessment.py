from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

from app.models.common import AssessmentMode, AssessmentStatus, Language, RoleName, Sector


class AssessmentStartRequest(BaseModel):
    sector: Sector
    role: RoleName
    language: Language = Language.en
    mode: AssessmentMode = AssessmentMode.full


class DomainScore(BaseModel):
    domain: str
    maturity_score: float
    assurance_score: float
    control_count: int


class HighImpactGap(BaseModel):
    control_id: str
    title: str
    domain: str
    reason: str


class AssessmentOut(BaseModel):
    id: str
    organisation_id: str
    created_by: str
    sector: str
    role: str
    language: str
    mode: str = "full"
    status: AssessmentStatus
    progress: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    maturity_score: Optional[float] = None
    assurance_score: Optional[float] = None
    domain_scores: list[DomainScore] = []
    high_impact_gaps: list[HighImpactGap] = []
    total_controls: int = 0
    answered_controls: int = 0


class AnswerSubmitRequest(BaseModel):
    control_id: str
    answer: Any


class AnswerOut(BaseModel):
    id: str
    assessment_id: str
    question_id: str
    control_id: str
    answer: Any
    score: float
    weight: float
    impact_level: str
    answered_by: str
    answered_at: datetime
