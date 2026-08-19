"""A4 — Verification Probe ingest + signature verification. The backend never
trusts probe output unless the Ed25519 signature validates against the known
probe public key."""
from pathlib import Path

from app.core.crypto import get_probe_private_key_pem, load_or_create_probe_keypair, verify_probe_signature
from app.models.probe import ProbeIngestRequest
from app.repositories.collections import probe_checks_repo, probe_runs_repo
from app.services import assessment_service, scoring_service

CHECK_DEFINITIONS = {
    "CHECK_001": {"label": "SMBv1 protocol disabled", "control_id": "PROBE-SMBV1"},
    "CHECK_002": {"label": "RDP not openly exposed / NLA enforced", "control_id": "PROBE-RDP-EXPOSURE"},
    "CHECK_003": {"label": "Backup destination writable (from this host)", "control_id": "PROBE-BACKUP-WRITABLE"},
    "CHECK_004": {"label": "Volume Shadow Copy service state", "control_id": "PROBE-VSS-SERVICE"},
    "CHECK_005": {"label": "AV/EDR service running", "control_id": "PROBE-AVEDR-SERVICE"},
    "CHECK_006": {"label": "NTP time synchronization active", "control_id": "PROBE-NTP-SYNC"},
    "CHECK_007": {"label": "Host firewall enabled", "control_id": "PROBE-FIREWALL"},
    "CHECK_008": {"label": "OS patch recency within threshold", "control_id": "PROBE-PATCH-RECENCY"},
    "CHECK_009": {"label": "Local administrator account count reasonable", "control_id": "PROBE-LOCAL-ADMINS"},
    "CHECK_010": {"label": "Screen-lock / idle-timeout policy configured", "control_id": "PROBE-SCREEN-LOCK"},
    "CHECK_011": {"label": "Remote Registry service disabled", "control_id": "PROBE-REMOTE-REGISTRY"},
    "CHECK_012": {"label": "Disk encryption enabled", "control_id": "PROBE-DISK-ENCRYPTION"},
}


def get_probe_public_key_b64() -> str:
    _, public_key_b64 = load_or_create_probe_keypair()
    return public_key_b64


def ingest_probe_result(payload: ProbeIngestRequest) -> dict:
    assessment = assessment_service.get_assessment(payload.assessment_id)
    _, public_key_b64 = load_or_create_probe_keypair()

    message = f"{payload.assessment_id}|{payload.host_fingerprint}|{payload.timestamp}|{payload.checks_raw}"
    signature_valid = verify_probe_signature(message.encode("utf-8"), payload.signature, public_key_b64)

    probe_run_id = probe_runs_repo.insert(
        {
            "assessment_id": payload.assessment_id,
            "organisation_id": assessment["organisation_id"],
            "host_fingerprint": payload.host_fingerprint,
            "timestamp": payload.timestamp,
            "signature": payload.signature,
            "public_key_id": public_key_b64[:16],
            "verification_status": "verified" if signature_valid else "rejected",
            "raw_result_object_key": None,
        }
    )

    for check in payload.checks:
        definition = CHECK_DEFINITIONS.get(check.check_id, {})
        probe_checks_repo.insert(
            {
                "probe_run_id": probe_run_id,
                "check_id": check.check_id,
                "result": check.result,
                "details": check.details or {},
                "timestamp": check.timestamp,
                "label": definition.get("label", check.check_id),
                "control_id": definition.get("control_id"),
            }
        )

    if signature_valid:
        scoring_service.recompute_assessment_scores(payload.assessment_id)

    return get_probe_run(probe_run_id)


def get_probe_run(probe_run_id: str) -> dict:
    run = probe_runs_repo.get_by_id(probe_run_id)
    checks = probe_checks_repo.find({"probe_run_id": probe_run_id})
    run["checks"] = checks
    return run


def list_probe_runs(assessment_id: str) -> list[dict]:
    runs = probe_runs_repo.find({"assessment_id": assessment_id}, sort=[("created_at", -1)])
    for run in runs:
        run["checks"] = probe_checks_repo.find({"probe_run_id": run["id"]})
    return runs


PROBE_TEMPLATE_DIR = Path(__file__).resolve().parent.parent.parent / "probes"


def _render_template(template_filename: str, backend_url: str) -> str:
    template_path = PROBE_TEMPLATE_DIR / template_filename
    text = template_path.read_text(encoding="utf-8")
    private_key_pem = get_probe_private_key_pem()
    text = text.replace("__PROBE_PRIVATE_KEY_PEM__", private_key_pem)
    text = text.replace("__BACKEND_URL__", backend_url)
    return text


def render_powershell_script(backend_url: str) -> str:
    return _render_template("verify_probe.ps1.tmpl", backend_url)


def render_bash_script(backend_url: str) -> str:
    return _render_template("verify_probe.sh.tmpl", backend_url)
