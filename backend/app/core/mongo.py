from functools import lru_cache

from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.database import Database

from app.core.config import get_settings


@lru_cache
def get_client() -> MongoClient:
    settings = get_settings()
    return MongoClient(settings.mongodb_uri, uuidRepresentation="standard")


def get_db() -> Database:
    settings = get_settings()
    return get_client()[settings.mongodb_db_name]


def ensure_indexes() -> None:
    db = get_db()

    db.users.create_index([("email", ASCENDING)], unique=True)
    db.users.create_index([("organisation_id", ASCENDING)])

    db.organisations.create_index([("name", ASCENDING)])
    db.organisations.create_index([("sector", ASCENDING)])

    db.questions.create_index([("control_id", ASCENDING)], unique=True)
    db.questions.create_index([("domain", ASCENDING)])
    db.questions.create_index([("sector", ASCENDING)])
    db.questions.create_index([("roles", ASCENDING)])
    db.questions.create_index([("active", ASCENDING)])

    db.assessments.create_index([("organisation_id", ASCENDING)])
    db.assessments.create_index([("status", ASCENDING)])
    db.assessments.create_index([("completed_at", DESCENDING)])

    db.answers.create_index([("assessment_id", ASCENDING)])
    db.answers.create_index([("control_id", ASCENDING)])
    db.answers.create_index([("assessment_id", ASCENDING), ("control_id", ASCENDING)], unique=True)

    db.evidence.create_index([("assessment_id", ASCENDING)])
    db.evidence.create_index([("control_id", ASCENDING)])
    db.evidence.create_index([("organisation_id", ASCENDING)])

    db.probe_runs.create_index([("assessment_id", ASCENDING)])
    db.probe_checks.create_index([("probe_run_id", ASCENDING)])

    db.detection_coverage.create_index([("assessment_id", ASCENDING)])
    db.log_sources.create_index([("assessment_id", ASCENDING)])
    db.canary_events.create_index([("organisation_id", ASCENDING)])
    db.canary_events.create_index([("timestamp", DESCENDING)])

    db.remediation_items.create_index([("assessment_id", ASCENDING)])

    db.reports.create_index([("assessment_id", ASCENDING)])

    db.ledger_entries.create_index([("assessment_id", ASCENDING)])
    db.ledger_entries.create_index([("timestamp", DESCENDING)])
    # Sequence is only unique *within* an organisation's own chain — each org
    # has its own independent hash chain, so sequence numbers repeat across
    # organisations by design. Drop the old single-field unique index (from
    # when the ledger was one global chain) if a pre-existing database still
    # has it, since it would otherwise still reject same-sequence entries
    # across different orgs.
    existing_index_names = {idx["name"] for idx in db.ledger_entries.list_indexes()}
    if "sequence_1" in existing_index_names:
        db.ledger_entries.drop_index("sequence_1")
    db.ledger_entries.create_index([("organisation_id", ASCENDING), ("sequence", ASCENDING)], unique=True)

    db.audit_logs.create_index([("organisation_id", ASCENDING)])
    db.audit_logs.create_index([("timestamp", DESCENDING)])

    db.scoring_configs.create_index([("active", ASCENDING)])
