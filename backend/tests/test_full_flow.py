"""Integration test covering the full spec §36 flow end-to-end through the
real API surface: register -> org -> start assessment -> answer -> evidence
-> probe ingest -> scores -> roadmap -> report -> ledger entry -> verify."""
import base64

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.core.crypto import load_or_create_probe_keypair
from app.repositories.collections import questions_repo, scoring_configs_repo
from tests.conftest import auth_headers, register_org


def _seed_question_bank():
    scoring_configs_repo.insert(
        {
            "version": 1,
            "domains": ["Backup & Recovery", "Identity & Access Management"],
            "impact_multipliers": {"low": 1.0, "medium": 1.5, "high": 2.0},
            "assurance_rules": {
                "unverified_claim_weight": 0.35,
                "evidence_weight": 0.75,
                "evidence_verified_weight": 0.9,
                "probe_verified_weight": 1.0,
                "high_impact_assurance_threshold": 0.6,
            },
            "active": True,
        }
    )
    questions_repo.insert(
        {
            "control_id": "IT-BACKUP-TESTED", "title": {"en": "Backups are restore-tested"},
            "domain": "Backup & Recovery", "sector": "generic", "roles": ["it_administrator"],
            "answer_type": "boolean", "options": [], "weight": 2.0, "impact_level": "high",
            "evidence_required": True,
            "micro_learning": {
                "en": {
                    "why_it_matters": "Untested backups may not actually restore.",
                    "risk_addressed": "Backups reachable from production are often encrypted by ransomware.",
                    "good_practice": "Test restores quarterly.",
                    "evidence_hint": "Upload the most recent restore-test report.",
                }
            },
            "probe_check_id": "CHECK_003", "active": True,
        }
    )
    questions_repo.insert(
        {
            "control_id": "IT-MFA", "title": {"en": "MFA enforced"},
            "domain": "Identity & Access Management", "sector": "generic", "roles": ["it_administrator"],
            "answer_type": "boolean", "options": [], "weight": 1.5, "impact_level": "medium",
            "evidence_required": False, "active": True,
        }
    )


def _sign(message: str, private_key_b64: str) -> str:
    raw = base64.b64decode(private_key_b64)
    key = Ed25519PrivateKey.from_private_bytes(raw)
    return base64.b64encode(key.sign(message.encode("utf-8"))).decode()


def test_full_assessment_lifecycle(client, monkeypatch):
    from app.services import evidence_service, report_service

    class _StubHTML:
        def __init__(self, *a, **k):
            pass

        def write_pdf(self):
            return b"%PDF-1.4 stub"

    # report_service imports weasyprint.HTML lazily, inside generate_report()
    # itself (not at module level), so it can boot on hosts without
    # WeasyPrint's native libs installed — patch it at its source instead.
    monkeypatch.setattr("weasyprint.HTML", _StubHTML)
    monkeypatch.setattr(report_service, "put_object", lambda *a, **k: None)
    monkeypatch.setattr(report_service, "presigned_get_url", lambda *a, **k: "http://stub/report.pdf")
    monkeypatch.setattr(report_service, "ensure_buckets", lambda: None)
    monkeypatch.setattr(evidence_service, "put_object", lambda *a, **k: None)
    monkeypatch.setattr(evidence_service, "presigned_get_url", lambda *a, **k: "http://stub/evidence")
    monkeypatch.setattr(evidence_service, "ensure_buckets", lambda: None)

    _seed_question_bank()
    auth = register_org(client, name="Full Flow Org", sector="generic", email="flow@org.com")
    token = auth["access_token"]

    start = client.post("/assessments/start", json={"sector": "generic", "role": "it_administrator", "language": "en"}, headers=auth_headers(token))
    assert start.status_code == 200
    assessment_id = start.json()["id"]
    assert start.json()["total_controls"] == 2

    ans1 = client.post(f"/assessments/{assessment_id}/answers", json={"control_id": "IT-BACKUP-TESTED", "answer": True}, headers=auth_headers(token))
    assert ans1.status_code == 200
    ans2 = client.post(f"/assessments/{assessment_id}/answers", json={"control_id": "IT-MFA", "answer": True}, headers=auth_headers(token))
    assert ans2.status_code == 200

    evidence_resp = client.post(
        f"/evidence/{assessment_id}/IT-BACKUP-TESTED",
        files={"file": ("restore-test.pdf", b"%PDF-1.4 fake evidence content", "application/pdf")},
        headers=auth_headers(token),
    )
    assert evidence_resp.status_code == 200

    priv_b64, _ = load_or_create_probe_keypair()
    checks_raw = '[{"check_id":"CHECK_003","result":"pass","details":{},"timestamp":"2026-01-01T00:00:00Z"}]'
    host_fingerprint = "test-host-fp"
    timestamp = "2026-01-01T00:00:00Z"
    message = f"{assessment_id}|{host_fingerprint}|{timestamp}|{checks_raw}"
    signature = _sign(message, priv_b64)

    probe_resp = client.post(
        "/probe/ingest",
        json={
            "assessment_id": assessment_id, "host_fingerprint": host_fingerprint, "timestamp": timestamp,
            "checks": [{"check_id": "CHECK_003", "result": "pass", "details": {}, "timestamp": timestamp}],
            "checks_raw": checks_raw, "signature": signature,
        },
        headers=auth_headers(token),
    )
    assert probe_resp.status_code == 200
    assert probe_resp.json()["verification_status"] == "verified"

    complete = client.post(f"/assessments/{assessment_id}/complete", headers=auth_headers(token))
    assert complete.status_code == 200
    completed = complete.json()
    assert completed["status"] == "completed"
    assert completed["maturity_score"] > 0
    assert completed["assurance_score"] > 0

    dashboard = client.get(f"/dashboard/{assessment_id}", headers=auth_headers(token))
    assert dashboard.status_code == 200
    assert dashboard.json()["assessment"]["status"] == "completed"

    roadmap = client.post(f"/remediation/{assessment_id}/generate", headers=auth_headers(token))
    assert roadmap.status_code == 200

    report = client.post(f"/reports/{assessment_id}/generate", json={"report_type": "executive"}, headers=auth_headers(token))
    assert report.status_code == 200
    assert report.json()["version"] == 1

    ledger_entries = client.get("/ledger/entries", headers=auth_headers(token))
    assert ledger_entries.status_code == 200
    assert len(ledger_entries.json()) >= 2  # one for assessment completion, one for the report

    verify = client.post("/ledger/verify", headers=auth_headers(token))
    assert verify.status_code == 200
    assert verify.json()["verified"] is True
