from datetime import date
from typing import Optional

from pydantic import BaseModel


class BackupResilienceIn(BaseModel):
    backup_destination: str
    is_writable_from_production: bool
    backup_frequency: str
    last_successful_backup: Optional[date] = None
    last_restore_test: Optional[date] = None
    restore_test_owner: Optional[str] = None
    recovery_confidence: int  # 1-5


class BackupResilienceOut(BackupResilienceIn):
    id: str
    assessment_id: str
    organisation_id: str
    restore_test_gap: bool
    risk_note: str
