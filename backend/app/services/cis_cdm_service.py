"""CIS Community Defense Model v2.0 traceability. The ransomware-specific,
per-ATT&CK-tactic coverage table (cis_cdm_ransomware_tactic_coverage) was
pulled directly from the primary-source PDF and cross-checked against the
extracted text before being hard-coded here — see the comment above
CIS_CDM_REFERENCE in app/seed/questions_data.py for full provenance.
"""
from app.models.common import KillChainStage
from app.seed.questions_data import cis_cdm_ransomware_tactic_coverage

# Our 5-stage kill chain (app/models/common.py KillChainStage) maps onto
# CDM's 14 ATT&CK tactics as follows. Shadow Copy Deletion isn't its own
# ATT&CK tactic — the relevant techniques (T1490 Inhibit System Recovery,
# T1489 Service Stop) fall under the "impact" tactic, so that's the closest
# real CDM figure available for that stage.
STAGE_TO_CDM_TACTIC: dict[str, str] = {
    KillChainStage.credential_access.value: "credential-access",
    KillChainStage.discovery.value: "discovery",
    KillChainStage.lateral_movement.value: "lateral-movement",
    KillChainStage.shadow_copy_deletion.value: "impact",
    KillChainStage.exfiltration.value: "exfiltration",
}


def get_stage_benchmark(stage: str) -> dict | None:
    """CDM's published ransomware-pattern coverage percentage for the
    ATT&CK tactic behind this stage — an external, industry benchmark to
    sit alongside this organisation's own computed log_coverage, not a
    replacement for it."""
    tactic = STAGE_TO_CDM_TACTIC.get(stage)
    if not tactic:
        return None
    data = cis_cdm_ransomware_tactic_coverage()
    pct = data["by_tactic_pct"].get(tactic)
    if pct is None:
        return None
    return {"tactic": tactic, "coverage_pct": pct, "source": data["source"]}


def get_full_reference() -> dict:
    return cis_cdm_ransomware_tactic_coverage()
