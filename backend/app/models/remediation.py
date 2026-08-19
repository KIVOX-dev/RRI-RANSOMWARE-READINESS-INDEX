from pydantic import BaseModel

from app.models.common import EffortLevel, ImpactLevel, RemediationPriority


class RemediationItemOut(BaseModel):
    id: str
    assessment_id: str
    control_id: str
    issue: str
    domain: str
    impact: ImpactLevel
    effort: EffortLevel
    priority: RemediationPriority
    reason: str
    recommended_action: str
    status: str = "open"
