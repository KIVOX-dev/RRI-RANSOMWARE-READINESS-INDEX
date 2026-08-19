from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class ProbeCheckIn(BaseModel):
    check_id: str
    result: str
    details: Optional[dict[str, Any]] = None
    timestamp: str


class ProbeIngestRequest(BaseModel):
    assessment_id: str
    host_fingerprint: str
    timestamp: str
    checks: list[ProbeCheckIn]
    checks_raw: str  # exact compact-JSON text of `checks` as signed by the probe script
    signature: str


class ProbeCheckOut(BaseModel):
    check_id: str
    result: str
    details: Optional[dict[str, Any]] = None
    timestamp: str
    label: Optional[str] = None
    control_id: Optional[str] = None


class ProbeRunOut(BaseModel):
    id: str
    assessment_id: str
    organisation_id: str
    host_fingerprint: str
    timestamp: str
    verification_status: str
    checks: list[ProbeCheckOut] = []
    created_at: datetime
    note: str = (
        "A valid signature proves this output came from the official RRI verification probe script. "
        "It does not prove the host itself was uncompromised before the script ran."
    )
