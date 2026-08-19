from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.common import EvidenceStatus


class EvidenceOut(BaseModel):
    id: str
    assessment_id: str
    organisation_id: str
    control_id: str
    filename: str
    object_key: str
    mime_type: str
    size: int
    checksum: str
    uploaded_by: str
    verification_status: EvidenceStatus
    created_at: datetime
    download_url: Optional[str] = None
