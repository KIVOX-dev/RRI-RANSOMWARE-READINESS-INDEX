from datetime import datetime

from pydantic import BaseModel


class ReportOut(BaseModel):
    id: str
    assessment_id: str
    organisation_id: str
    report_type: str
    version: int
    object_key: str
    checksum: str
    generated_at: datetime
    status: str
    download_url: str | None = None


class ReportGenerateRequest(BaseModel):
    report_type: str = "executive"
