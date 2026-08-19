"""B3 — Canary Tripwire Kit. Deploys real decoy files on the backend host,
runs a background watcher thread that polls their content hash, and on a
change writes a canary_events document + publishes it over Redis pub/sub for
the SSE dashboard stream. Clearly labeled as a local simulated watcher — for
a hosted demo there is no real endpoint to plant files on, so the "protected
host" is the backend container's own filesystem.
"""
import hashlib
import json
import random
import threading
import time
from pathlib import Path

from app.core.cache import get_redis
from app.repositories.base import now_utc
from app.repositories.collections import Repository, canary_events_repo

CANARY_DIR = Path(__file__).resolve().parent.parent / "static" / "canary_decoys"

DECOY_NAMES = [
    "Payroll_2026_Q1_CONFIDENTIAL.xlsx",
    "Employee_SSN_Records.docx",
    "Executive_Passwords_Backup.txt",
    "Client_Database_Export.csv",
    "M&A_Term_Sheet_DRAFT.pdf",
    "Board_Meeting_Minutes.docx",
    "Server_Credentials.txt",
    "Insurance_Claims_2026.xlsx",
]

DECOY_CONTENT = (
    "This is a synthetic decoy file created by the RRI Canary Tripwire Kit for local ransomware-readiness "
    "demonstration purposes only. It contains no real data. Any modification, deletion, or encryption of "
    "this file is treated as a tripwire event.\n"
)


class CanaryRegistryRepo(Repository):
    collection_name = "canary_registry"


canary_registry_repo = CanaryRegistryRepo()

_watcher_started = False
_watcher_lock = threading.Lock()


def _file_hash(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    return hashlib.sha256(path.read_bytes()).hexdigest()


def deploy_canaries(organisation_id: str, assessment_id: str | None, count: int = 5) -> list[dict]:
    CANARY_DIR.mkdir(parents=True, exist_ok=True)
    org_dir = CANARY_DIR / organisation_id
    org_dir.mkdir(parents=True, exist_ok=True)

    names = random.sample(DECOY_NAMES, min(count, len(DECOY_NAMES)))
    deployed = []
    for name in names:
        file_path = org_dir / name
        file_path.write_text(DECOY_CONTENT, encoding="utf-8")
        canary_id = f"canary-{organisation_id[-6:]}-{hashlib.sha1(name.encode()).hexdigest()[:8]}"
        doc = {
            "canary_id": canary_id,
            "organisation_id": organisation_id,
            "assessment_id": assessment_id,
            "file_path": str(file_path),
            "baseline_hash": _file_hash(file_path),
            "status": "armed",
        }
        existing = canary_registry_repo.find_one({"canary_id": canary_id})
        if existing:
            canary_registry_repo.update_by_id(existing["id"], doc)
        else:
            canary_registry_repo.insert(doc)
        deployed.append(canary_registry_repo.find_one({"canary_id": canary_id}))
    return deployed


def list_canaries(organisation_id: str) -> list[dict]:
    return canary_registry_repo.find({"organisation_id": organisation_id})


def _publish(organisation_id: str, event: dict) -> None:
    try:
        get_redis().publish(f"canary_events:{organisation_id}", json.dumps(event, default=str))
    except Exception:
        pass  # SSE is a convenience layer; event is already persisted to Mongo


def _record_event(canary: dict, event_type: str, severity: str) -> dict:
    doc = {
        "organisation_id": canary["organisation_id"],
        "assessment_id": canary.get("assessment_id"),
        "canary_id": canary["canary_id"],
        "event_type": event_type,
        "file_path": canary["file_path"],
        "timestamp": now_utc(),
        "severity": severity,
        "status": "new",
    }
    event_id = canary_events_repo.insert(doc)
    event = canary_events_repo.get_by_id(event_id)
    canary_registry_repo.update_by_id(canary["id"], {"status": "tripped"})
    _publish(canary["organisation_id"], event)
    return event


def simulate_touch(canary_id: str) -> dict:
    """Demo-only: simulates an attacker touching/encrypting a canary file so
    the tripwire fires immediately rather than waiting for the poll cycle."""
    canary = canary_registry_repo.find_one({"canary_id": canary_id})
    if not canary:
        raise ValueError("Canary not found")
    path = Path(canary["file_path"])
    path.write_text(DECOY_CONTENT + f"\n[SIMULATED TAMPER {now_utc().isoformat()}]\n.encrypted", encoding="utf-8")
    return _record_event(canary, "simulated_encryption_pattern", "critical")


def list_events(organisation_id: str) -> list[dict]:
    return canary_events_repo.find({"organisation_id": organisation_id}, sort=[("timestamp", -1)])


def _watch_loop(poll_seconds: int = 5) -> None:
    while True:
        try:
            for canary in canary_registry_repo.find({"status": "armed"}):
                current_hash = _file_hash(Path(canary["file_path"]))
                if current_hash != canary["baseline_hash"]:
                    event_type = "deleted" if current_hash == "MISSING" else "modified"
                    _record_event(canary, event_type, "high")
        except Exception:
            pass
        time.sleep(poll_seconds)


def start_watcher_thread() -> None:
    global _watcher_started
    with _watcher_lock:
        if _watcher_started:
            return
        thread = threading.Thread(target=_watch_loop, daemon=True)
        thread.start()
        _watcher_started = True
