"""Default Integrity Ledger — an append-only, Ed25519-signed SHA-256 hash
chain. This is NOT a blockchain; it is a local signed hash chain used as the
application's default integrity mechanism, and it is fully self-sufficient.
The optional Hyperledger Fabric anchor (services/fabric_service.py) is a
separate stretch layer: every entry is *also* best-effort anchored on a
local Fabric network, but if that layer is unreachable, fabric_anchor simply
stays null — the hash chain itself never depends on it.

Each organisation has its own independent chain — sequence numbers and
previous_record_hash links only ever connect entries within the same
organisation_id, never across organisations, and Verify only ever
recomputes/checks the caller's own chain. A sub-organisation relationship
(organisations.parent_organisation_id) only ever affects *read* visibility,
one direction only: once verified, a parent's combined Ledger view also
includes each of its sub-organisations' entries (many-to-one), but a
sub-organisation never sees its parent's entries back — it never merges the
chains themselves either way.
"""
from app.core.crypto import canonical_json_bytes, compute_record_hash, sha256_hex, sign_ledger_record, verify_ledger_signature
from app.models.common import OrganisationVerificationStatus
from app.models.ledger import LedgerVerifyResult
from app.repositories.base import now_utc
from app.repositories.collections import ledger_entries_repo, organisations_repo
from app.services import fabric_service

GENESIS_HASH = "0" * 64


def _last_entry(organisation_id: str) -> dict | None:
    entries = ledger_entries_repo.find({"organisation_id": organisation_id}, sort=[("sequence", -1)], limit=1)
    return entries[0] if entries else None


def _visible_organisation_ids(organisation_id: str) -> list[str]:
    """The calling org's own id, plus — one direction only — any *verified*
    sub-organisations' ids. Many-to-one: a parent sees every one of its
    verified sub-orgs' entries in its combined Ledger view, but a sub-org
    never sees its parent's entries, and never sees sibling sub-orgs under
    the same parent either."""
    visible = {organisation_id}
    children = organisations_repo.find(
        {"parent_organisation_id": organisation_id, "verification_status": OrganisationVerificationStatus.verified.value}
    )
    visible.update(child["id"] for child in children)
    return list(visible)


def list_entries(organisation_id: str) -> list[dict]:
    org_ids = _visible_organisation_ids(organisation_id)
    entries = ledger_entries_repo.find({"organisation_id": {"$in": org_ids}}, sort=[("timestamp", 1)])

    names: dict[str, str] = {}
    for org_id in org_ids:
        org = organisations_repo.get_by_id(org_id)
        names[org_id] = org.get("name", "Unknown") if org else "Unknown"
    for entry in entries:
        entry["organisation_name"] = names.get(entry["organisation_id"], "Unknown")
    return entries


def create_ledger_entry(
    organisation_id: str,
    payload: dict,
    assessment_id: str | None = None,
    report_id: str | None = None,
    record_type: str = "standard",
    sub_organisation_id: str | None = None,
) -> dict:
    payload_hash = sha256_hex(canonical_json_bytes(payload))
    last = _last_entry(organisation_id)
    prev_hash = last["record_hash"] if last else GENESIS_HASH
    sequence = (last["sequence"] + 1) if last else 1
    record_hash = compute_record_hash(payload_hash, prev_hash)
    signature = sign_ledger_record(record_hash)
    fabric_anchor = fabric_service.anchor_on_chain(record_hash)

    entry_id = ledger_entries_repo.insert(
        {
            "organisation_id": organisation_id,
            "sequence": sequence,
            "assessment_id": assessment_id,
            "report_id": report_id,
            "timestamp": now_utc(),
            "payload_hash": payload_hash,
            "previous_record_hash": prev_hash,
            "record_hash": record_hash,
            "signature": signature,
            "fabric_anchor": fabric_anchor,
            "verification_status": "unverified",
            "record_type": record_type,
            "sub_organisation_id": sub_organisation_id,
        }
    )
    entry = ledger_entries_repo.get_by_id(entry_id)
    org = organisations_repo.get_by_id(organisation_id)
    entry["organisation_name"] = org.get("name", "Unknown") if org else "Unknown"
    return entry


def verify_chain(organisation_id: str) -> LedgerVerifyResult:
    entries = ledger_entries_repo.find({"organisation_id": organisation_id}, sort=[("sequence", 1)])
    prev_hash = GENESIS_HASH
    for entry in entries:
        expected_record_hash = compute_record_hash(entry["payload_hash"], prev_hash)
        broken = False
        reason = ""
        if entry["previous_record_hash"] != prev_hash:
            broken = True
            reason = "previous_record_hash does not match the prior record"
        elif entry["record_hash"] != expected_record_hash:
            broken = True
            reason = "record_hash does not match recomputed hash of stored payload_hash + previous_record_hash"
        elif not verify_ledger_signature(entry["record_hash"], entry["signature"]):
            broken = True
            reason = "Ed25519 signature does not validate against the ledger record"

        if broken:
            ledger_entries_repo.update_by_id(entry["id"], {"verification_status": "invalid"})
            for later in entries:
                if later["sequence"] > entry["sequence"]:
                    ledger_entries_repo.update_by_id(later["id"], {"verification_status": "unverified"})
            return LedgerVerifyResult(
                verified=False,
                total_records=len(entries),
                broken_at_sequence=entry["sequence"],
                message=f"Integrity Violation Detected at record #{entry['sequence']}: {reason}.",
            )
        ledger_entries_repo.update_by_id(entry["id"], {"verification_status": "verified"})
        prev_hash = entry["record_hash"]

    return LedgerVerifyResult(
        verified=True,
        total_records=len(entries),
        broken_at_sequence=None,
        message="Integrity Verified: all records form an unbroken, correctly signed hash chain.",
    )


def verify_chain_and_process_approvals(organisation_id: str) -> LedgerVerifyResult:
    """Verify's normal cryptographic result, plus a side effect: a verified
    chain is also the trigger that approves any pending sub-organisation
    requests recorded in it (see auth_service.register). This keeps
    verify_chain() itself a pure integrity check while giving the Verify
    button real business meaning for organisations with pending sub-org
    requests."""
    result = verify_chain(organisation_id)
    if not result.verified:
        return result

    pending_requests = ledger_entries_repo.find(
        {"organisation_id": organisation_id, "record_type": "sub_organisation_request"}
    )
    for request in pending_requests:
        sub_org_id = request.get("sub_organisation_id")
        if not sub_org_id:
            continue
        sub_org = organisations_repo.get_by_id(sub_org_id)
        if not sub_org or sub_org.get("verification_status") != OrganisationVerificationStatus.pending.value:
            continue
        organisations_repo.update_by_id(sub_org_id, {"verification_status": OrganisationVerificationStatus.verified.value})
        create_ledger_entry(
            sub_org_id,
            {"type": "sub_organisation_verified_by_parent", "parent_organisation_id": organisation_id},
            record_type="standard",
        )
    return result


def demo_tamper(organisation_id: str, entry_sequence: int) -> dict:
    """Admin/demo-only: intentionally corrupts a stored payload_hash so the
    next verify_chain() call demonstrates Integrity Violation Detected."""
    entries = ledger_entries_repo.find({"organisation_id": organisation_id, "sequence": entry_sequence})
    if not entries:
        raise ValueError("Ledger entry not found")
    entry = entries[0]
    tampered_hash = sha256_hex(f"tampered-{entry['payload_hash']}".encode())
    ledger_entries_repo.update_by_id(entry["id"], {"payload_hash": tampered_hash, "verification_status": "unverified"})
    updated = ledger_entries_repo.get_by_id(entry["id"])
    org = organisations_repo.get_by_id(organisation_id)
    updated["organisation_name"] = org.get("name", "Unknown") if org else "Unknown"
    return updated
