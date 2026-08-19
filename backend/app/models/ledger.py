from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LedgerEntryOut(BaseModel):
    id: str
    organisation_id: str
    organisation_name: str
    sequence: int
    assessment_id: Optional[str] = None
    report_id: Optional[str] = None
    timestamp: datetime
    payload_hash: str
    previous_record_hash: str
    record_hash: str
    signature: str
    fabric_anchor: Optional[str] = None
    verification_status: str = "unverified"
    record_type: str = "standard"
    sub_organisation_id: Optional[str] = None


class LedgerVerifyResult(BaseModel):
    verified: bool
    total_records: int
    broken_at_sequence: Optional[int] = None
    message: str
