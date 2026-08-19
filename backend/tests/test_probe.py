import base64

from app.core.crypto import load_or_create_probe_keypair, verify_probe_signature
from app.models.probe import ProbeCheckIn, ProbeIngestRequest
from app.repositories.collections import assessments_repo, organisations_repo, users_repo
from app.services import probe_service
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def _sign(message: str, private_key_b64: str) -> str:
    raw = base64.b64decode(private_key_b64)
    key = Ed25519PrivateKey.from_private_bytes(raw)
    return base64.b64encode(key.sign(message.encode("utf-8"))).decode()


def _make_assessment():
    org_id = organisations_repo.insert({"name": "Probe Org", "sector": "generic", "is_synthetic": False})
    user_id = users_repo.insert({"organisation_id": org_id, "name": "T", "email": "p@p.com", "password_hash": "x", "role": "org_admin", "language": "en", "status": "active"})
    assessment_id = assessments_repo.insert(
        {"organisation_id": org_id, "created_by": user_id, "sector": "generic", "role": "it_administrator",
         "language": "en", "status": "in_progress", "progress": 0, "total_controls": 0, "answered_controls": 0,
         "domain_scores": [], "high_impact_gaps": []}
    )
    return assessment_id


def test_valid_signature_round_trips():
    priv_b64, pub_b64 = load_or_create_probe_keypair()
    message = "hello-world"
    signature = _sign(message, priv_b64)
    assert verify_probe_signature(message.encode(), signature, pub_b64) is True


def test_tampered_message_fails_verification():
    priv_b64, pub_b64 = load_or_create_probe_keypair()
    signature = _sign("original-message", priv_b64)
    assert verify_probe_signature(b"tampered-message", signature, pub_b64) is False


def test_probe_ingest_accepts_valid_signature():
    assessment_id = _make_assessment()
    priv_b64, _ = load_or_create_probe_keypair()

    checks_raw = '[{"check_id":"CHECK_007","result":"pass","details":{},"timestamp":"2026-01-01T00:00:00Z"}]'
    timestamp = "2026-01-01T00:00:00Z"
    host_fingerprint = "abc123"
    message = f"{assessment_id}|{host_fingerprint}|{timestamp}|{checks_raw}"
    signature = _sign(message, priv_b64)

    payload = ProbeIngestRequest(
        assessment_id=assessment_id,
        host_fingerprint=host_fingerprint,
        timestamp=timestamp,
        checks=[ProbeCheckIn(check_id="CHECK_007", result="pass", details={}, timestamp=timestamp)],
        checks_raw=checks_raw,
        signature=signature,
    )
    result = probe_service.ingest_probe_result(payload)
    assert result["verification_status"] == "verified"


def test_probe_ingest_rejects_invalid_signature():
    assessment_id = _make_assessment()
    checks_raw = '[{"check_id":"CHECK_007","result":"pass","details":{},"timestamp":"2026-01-01T00:00:00Z"}]'
    payload = ProbeIngestRequest(
        assessment_id=assessment_id,
        host_fingerprint="abc123",
        timestamp="2026-01-01T00:00:00Z",
        checks=[ProbeCheckIn(check_id="CHECK_007", result="pass", details={}, timestamp="2026-01-01T00:00:00Z")],
        checks_raw=checks_raw,
        signature=base64.b64encode(b"not-a-real-signature-1234567890123456789012345678901234567890").decode(),
    )
    result = probe_service.ingest_probe_result(payload)
    assert result["verification_status"] == "rejected"
