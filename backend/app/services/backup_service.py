"""A5 — Backup Resilience Deep-Dive."""
from datetime import date

from app.models.backup import BackupResilienceIn
from app.repositories.collections import backup_resilience_repo


def upsert_backup_resilience(assessment_id: str, organisation_id: str, payload: BackupResilienceIn) -> dict:
    restore_test_gap = payload.last_restore_test is None
    if not restore_test_gap and payload.last_restore_test:
        days_since = (date.today() - payload.last_restore_test).days
        restore_test_gap = days_since > 180

    risk_note = (
        "No restore test on record — this is a high-priority remediation gap. A backup that has never been "
        "restored cannot be trusted for recovery."
        if payload.last_restore_test is None
        else (
            "Restore test is stale (over 180 days) — treat as a high-priority remediation gap."
            if restore_test_gap
            else "Restore testing is current."
        )
    )

    doc = {
        **payload.model_dump(mode="json"),
        "assessment_id": assessment_id,
        "organisation_id": organisation_id,
        "restore_test_gap": restore_test_gap,
        "risk_note": risk_note,
    }

    existing = backup_resilience_repo.find_one({"assessment_id": assessment_id})
    if existing:
        backup_resilience_repo.update_by_id(existing["id"], doc)
        return backup_resilience_repo.get_by_id(existing["id"])
    new_id = backup_resilience_repo.insert(doc)
    return backup_resilience_repo.get_by_id(new_id)


def get_backup_resilience(assessment_id: str) -> dict | None:
    return backup_resilience_repo.find_one({"assessment_id": assessment_id})
