"""Optional Hyperledger Fabric integrity-ledger stretch anchor (spec §21).

This is NOT the application's default integrity mechanism — that's the
signed, off-chain SHA-256 hash chain in ledger_service.py, which is fully
functional on its own. This module best-effort anchors each ledger record's
hash on a local, single-org Hyperledger Fabric network by calling a minimal
chaincode's `anchorAssessment` transaction. Any failure here (Fabric
unreachable, gateway error, etc.) is logged and swallowed — it must never
break the core ledger write, which is why this is called from ledger_service
with its result treated as optional.

Fabric's officially-supported client SDK (Fabric Gateway) ships Go, Node,
and Java clients only — not Python — so this module talks to a small Node.js
sidecar ("fabric-gateway-api") over plain HTTP instead of speaking the
Fabric Gateway/gRPC protocol directly. See fabric-gateway-api/ and
fabric-network/ for the rest of the network.
"""
import logging
import threading
import time

import httpx

from app.core.config import get_settings

logger = logging.getLogger("rri.fabric")

# Guards reconcile_from_ledger against running twice at once (e.g. the
# background poll thread and a manual/admin-triggered call overlapping) —
# concurrent sweeps both anchor against the same on-chain counter and cause
# avoidable MVCC conflicts, seen live when testing this.
_reconcile_lock = threading.Lock()


def is_available() -> bool:
    settings = get_settings()
    if not settings.fabric_enabled:
        return False
    try:
        resp = httpx.get(f"{settings.fabric_gateway_url}/status", timeout=4)
        return resp.is_success and resp.json().get("connected", False)
    except Exception:
        return False


def anchor_on_chain(record_hash_hex: str) -> str | None:
    """Best-effort. Returns the on-chain Fabric transaction ID, or None if
    the Fabric network is unreachable or the call fails for any reason.

    Retries once on a rejected commit: the chaincode keeps a single running
    counter (ANCHOR_COUNT), so two anchor calls landing close together can
    hit Fabric's optimistic-concurrency MVCC_READ_CONFLICT — the second
    transaction's endorsement was based on a counter value the first one
    already changed by the time it committed. This is expected, transient,
    and self-resolves once the other transaction has committed, which a
    short retry reliably catches (confirmed live: reconciling several
    records at once tripped this, and every conflict cleared on the next
    pass)."""
    settings = get_settings()
    if not settings.fabric_enabled:
        return None
    for attempt in range(2):
        try:
            resp = httpx.post(
                f"{settings.fabric_gateway_url}/anchor",
                json={"record_hash": record_hash_hex},
                timeout=10,
            )
            if resp.is_success:
                return resp.json().get("tx_id")
            if attempt == 0:
                time.sleep(0.5)
                continue
            logger.warning("Fabric anchor failed (non-fatal — the signed hash chain remains the source of truth): %s", resp.text)
            return None
        except Exception as exc:
            logger.warning("Fabric anchor failed (non-fatal — the signed hash chain remains the source of truth): %s", exc)
            return None
    return None


def get_chain_status() -> dict:
    """Read-only status for the Ledger page — is the optional anchor layer
    reachable, and how many anchors has it recorded so far."""
    settings = get_settings()
    if not settings.fabric_enabled:
        return {"enabled": False, "connected": False, "anchor_count": None, "contract_address": None}
    try:
        resp = httpx.get(f"{settings.fabric_gateway_url}/status", timeout=4)
        data = resp.json() if resp.is_success else {}
        return {
            "enabled": True,
            "connected": bool(data.get("connected")),
            "anchor_count": data.get("anchor_count"),
            "contract_address": "rri-anchor@rrichannel",
        }
    except Exception as exc:
        logger.warning("Fabric status check failed: %s", exc)
        return {"enabled": True, "connected": False, "anchor_count": None, "contract_address": "rri-anchor@rrichannel"}


def reconcile_from_ledger() -> int:
    """Fills in fabric_anchor for every ledger record that doesn't have one
    yet — covers both a freshly (re)started Fabric network with no on-chain
    history at all, and the narrower case of individual records that missed
    anchoring because Fabric happened to be unreachable at the moment they
    were created. MongoDB's ledger_entries collection (the real source of
    truth) already has every record_hash, so this is always safe to replay:
    anchoring is idempotent from the app's point of view (chaincode assigns
    a fresh index either way) and this only ever fills in a currently-null
    field, never overwrites an existing anchor. Runs every 60s via
    start_reconciliation_thread, so a null anchor is a transient state, not
    a permanent one, as long as Fabric comes back within a reasonable time.
    Best-effort like everything else in this module — never raises. Returns
    how many records were anchored.
    """
    from app.repositories.collections import ledger_entries_repo

    if not is_available():
        return 0
    if not _reconcile_lock.acquire(blocking=False):
        return 0  # another reconciliation pass is already in flight
    try:
        missing = ledger_entries_repo.find({"fabric_anchor": None}, sort=[("sequence", 1)])
        reanchored = 0
        for entry in missing:
            tx = anchor_on_chain(entry["record_hash"])
            if tx:
                ledger_entries_repo.update_by_id(entry["id"], {"fabric_anchor": tx})
                reanchored += 1
        if reanchored:
            logger.info("Reconciled %d ledger record(s) with a missing Fabric anchor.", reanchored)
        return reanchored
    except Exception as exc:
        logger.warning("Fabric reconciliation failed (non-fatal): %s", exc)
        return 0
    finally:
        _reconcile_lock.release()


def start_reconciliation_thread() -> None:
    """Runs for the lifetime of the backend process, not just once at
    startup — the Fabric network can lose chaincode state on its own at any
    point *after* the backend is already up and running, not just before.
    reconcile_from_ledger() is cheap and a no-op whenever every ledger entry
    already has a fabric_anchor, so polling it regularly costs almost
    nothing and makes the on-chain layer self-healing — any record created
    while Fabric was briefly unreachable gets anchored automatically within
    a minute, not only on a full backend restart."""

    def _run():
        settings = get_settings()
        if not settings.fabric_enabled:
            return
        # First few checks are frequent, since the Fabric network is often
        # still finishing its channel/chaincode setup when the backend
        # itself finishes booting.
        for _ in range(24):
            if is_available():
                reconcile_from_ledger()
                break
            time.sleep(5)
        while True:
            time.sleep(60)
            reconcile_from_ledger()

    threading.Thread(target=_run, daemon=True).start()
