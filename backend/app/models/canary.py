from datetime import datetime

from pydantic import BaseModel


class CanaryEventOut(BaseModel):
    id: str
    organisation_id: str
    assessment_id: str | None = None
    canary_id: str
    event_type: str
    file_path: str
    timestamp: datetime
    severity: str
    status: str
    simulated: bool = True


class CanaryDeploySettings(BaseModel):
    canary_count: int = 5
