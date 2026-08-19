from app.models.common import OrganisationVerificationStatus
from app.repositories.collections import organisations_repo
from app.services import ledger_service


def _make_org(name: str, parent_organisation_id: str | None = None) -> str:
    return organisations_repo.insert(
        {
            "name": name,
            "sector": "generic",
            "size": None,
            "location": None,
            "is_synthetic": False,
            "parent_organisation_id": parent_organisation_id,
            "verification_status": (
                OrganisationVerificationStatus.pending.value
                if parent_organisation_id
                else OrganisationVerificationStatus.verified.value
            ),
        }
    )


def test_ledger_chain_verifies_when_untampered():
    org = _make_org("Org 1")
    ledger_service.create_ledger_entry(org, {"a": 1}, assessment_id="assess-1")
    ledger_service.create_ledger_entry(org, {"b": 2}, assessment_id="assess-2")
    ledger_service.create_ledger_entry(org, {"c": 3}, assessment_id="assess-3")

    result = ledger_service.verify_chain(org)

    assert result.verified is True
    assert result.total_records == 3
    assert "Integrity Verified" in result.message


def test_ledger_chain_detects_tampering():
    org = _make_org("Org 2")
    ledger_service.create_ledger_entry(org, {"a": 1}, assessment_id="assess-1")
    ledger_service.create_ledger_entry(org, {"b": 2}, assessment_id="assess-2")

    ledger_service.demo_tamper(org, entry_sequence=1)
    result = ledger_service.verify_chain(org)

    assert result.verified is False
    assert result.broken_at_sequence == 1
    assert "Integrity Violation Detected" in result.message


def test_ledger_sequence_and_prev_hash_linkage():
    org = _make_org("Org 3")
    first = ledger_service.create_ledger_entry(org, {"a": 1}, assessment_id="assess-1")
    second = ledger_service.create_ledger_entry(org, {"b": 2}, assessment_id="assess-2")

    assert first["sequence"] == 1
    assert second["sequence"] == 2
    assert second["previous_record_hash"] == first["record_hash"]


def test_ledger_chains_are_isolated_per_organisation():
    org_a = _make_org("Org A")
    org_b = _make_org("Org B")

    a1 = ledger_service.create_ledger_entry(org_a, {"a": 1})
    b1 = ledger_service.create_ledger_entry(org_b, {"b": 1})
    a2 = ledger_service.create_ledger_entry(org_a, {"a": 2})

    assert a1["sequence"] == 1 and a2["sequence"] == 2
    assert b1["sequence"] == 1
    assert a2["previous_record_hash"] == a1["record_hash"]
    assert b1["previous_record_hash"] == ledger_service.GENESIS_HASH

    org_a_entries = ledger_service.list_entries(org_a)
    org_b_entries = ledger_service.list_entries(org_b)
    assert {e["id"] for e in org_a_entries} == {a1["id"], a2["id"]}
    assert {e["id"] for e in org_b_entries} == {b1["id"]}


def test_sub_organisation_request_verified_via_parent_verify_button():
    parent = _make_org("Parent Co")
    child = _make_org("Child Co", parent_organisation_id=parent)

    # Registration writes the request into the *parent's* ledger.
    ledger_service.create_ledger_entry(
        parent,
        {"type": "sub_organisation_request", "sub_organisation_id": child, "sub_organisation_name": "Child Co"},
        record_type="sub_organisation_request",
        sub_organisation_id=child,
    )

    assert organisations_repo.get_by_id(child)["verification_status"] == OrganisationVerificationStatus.pending.value
    assert ledger_service.list_entries(child) == []  # child not verified yet -> no shared visibility

    result = ledger_service.verify_chain_and_process_approvals(parent)
    assert result.verified is True

    child_org = organisations_repo.get_by_id(child)
    assert child_org["verification_status"] == OrganisationVerificationStatus.verified.value

    # The child's chain now has its own genesis entry from the approval.
    child_own_entries = ledger_service.list_entries(child)
    assert len(child_own_entries) == 1
    assert child_own_entries[0]["organisation_id"] == child

    # Many-to-one, one direction only: the parent's combined view includes
    # the child's entry, correctly labeled by organisation name...
    parent_entries = ledger_service.list_entries(parent)
    parent_org_ids = {e["organisation_id"] for e in parent_entries}
    assert child in parent_org_ids
    child_labeled = [e for e in parent_entries if e["organisation_id"] == child][0]
    assert child_labeled["organisation_name"] == "Child Co"

    # ...but the child never sees the parent's entries back.
    child_org_ids = {e["organisation_id"] for e in child_own_entries}
    assert parent not in child_org_ids
