"""B1 — ATT&CK-style detection coverage matrix and B2 — log gap analysis.
Both are pure derivations from stored answers + log_sources; nothing here
fabricates a capability that wasn't actually reported and evidenced."""
from app.models.common import KillChainStage
from app.models.detection import DetectionStageOut, LogGapAnalysisOut, LogSourceOut
from app.repositories.collections import answers_repo, log_sources_repo, questions_repo
from app.services import attck_service, cis_cdm_service

# Maps each kill-chain stage to the control_ids whose affirmative + evidenced/
# probe-verified answer demonstrates detection capability for that stage.
STAGE_CONTROL_MAP: dict[str, list[str]] = {
    KillChainStage.credential_access.value: ["LOG-AUTH-LOGGING", "IAM-MFA-ENFORCED", "LOG-EDR-CREDENTIAL-ALERTS"],
    KillChainStage.discovery.value: ["LOG-ENDPOINT-TELEMETRY", "NET-INTERNAL-MONITORING"],
    KillChainStage.lateral_movement.value: ["NET-SEGMENTATION", "LOG-NETWORK-FLOW", "IAM-PRIVILEGED-SESSION-MONITORING"],
    KillChainStage.shadow_copy_deletion.value: ["PROBE-VSS-SERVICE", "LOG-ENDPOINT-TELEMETRY", "BKP-IMMUTABLE-STORAGE"],
    KillChainStage.exfiltration.value: ["NET-DLP", "LOG-NETWORK-FLOW", "NET-EGRESS-FILTERING"],
}


def compute_detection_matrix(assessment_id: str) -> list[DetectionStageOut]:
    answers = {a["control_id"]: a for a in answers_repo.find({"assessment_id": assessment_id})}
    questions = {q["control_id"]: q for q in questions_repo.find({})}
    log_sources = log_sources_repo.find({"assessment_id": assessment_id})
    log_coverage_by_stage: dict[str, float] = {}
    for stage in STAGE_CONTROL_MAP:
        relevant = [ls for ls in log_sources if stage in ls.get("covered_stages", [])]
        enabled = [ls for ls in relevant if ls.get("enabled")]
        log_coverage_by_stage[stage] = (len(enabled) / len(relevant)) if relevant else 0.0

    results = []
    for stage, control_ids in STAGE_CONTROL_MAP.items():
        supporting = []
        strong_count = 0
        weak_count = 0
        for control_id in control_ids:
            answer = answers.get(control_id)
            if not answer or answer.get("score", 0) <= 0:
                continue
            supporting.append(control_id)
            # "Covered" requires affirmative answer AND some assurance signal (log coverage for this stage)
            if log_coverage_by_stage.get(stage, 0) > 0:
                strong_count += 1
            else:
                weak_count += 1

        if not supporting:
            status = "blind"
            explanation = "No answered controls in this assessment map to detection capability for this stage."
        elif strong_count >= 1 and log_coverage_by_stage.get(stage, 0) >= 0.5:
            status = "covered"
            explanation = f"{strong_count} supporting control(s) answered affirmatively with enabled log coverage for this stage."
        else:
            status = "partial"
            explanation = f"{len(supporting)} supporting control(s) answered affirmatively, but log coverage for this stage is incomplete."

        results.append(
            DetectionStageOut(
                stage=stage,
                status=status,
                supporting_controls=supporting,
                evidence_status="derived_from_answers_and_log_sources",
                log_coverage=round(log_coverage_by_stage.get(stage, 0.0) * 100, 1),
                explanation=explanation,
                attck_techniques=attck_service.techniques_for_stage(stage),
                cis_cdm_benchmark=cis_cdm_service.get_stage_benchmark(stage),
            )
        )
    return results


def upsert_log_sources(assessment_id: str, sources: list[dict]) -> list[LogSourceOut]:
    existing = {ls["source_name"]: ls for ls in log_sources_repo.find({"assessment_id": assessment_id})}
    out = []
    for src in sources:
        gaps = []
        if not src.get("enabled"):
            gaps.append("Source disabled")
        if src.get("retention_days", 0) < 90:
            gaps.append("Retention below recommended 90 days")
        if not src.get("monitored"):
            gaps.append("Not actively monitored")

        doc = {**src, "assessment_id": assessment_id, "gaps": gaps}
        if src["source_name"] in existing:
            log_sources_repo.update_by_id(existing[src["source_name"]]["id"], doc)
            out.append(log_sources_repo.get_by_id(existing[src["source_name"]]["id"]))
        else:
            new_id = log_sources_repo.insert(doc)
            out.append(log_sources_repo.get_by_id(new_id))
    return out


def get_log_gap_analysis(assessment_id: str) -> LogGapAnalysisOut:
    sources = log_sources_repo.find({"assessment_id": assessment_id})
    matrix = compute_detection_matrix(assessment_id)

    detectable = [s.stage for s in matrix if s.status == "covered"]
    partial = [s.stage for s in matrix if s.status == "partial"]
    blind = [s.stage for s in matrix if s.status == "blind"]

    retention_gaps = [s["source_name"] for s in sources if s.get("retention_days", 0) < 90]
    expected_sources = {
        "Endpoint/EDR telemetry", "Authentication logs", "Network flow logs",
        "Firewall logs", "DNS logs", "Backup system logs",
    }
    present_sources = {s["source_name"] for s in sources}
    missing_sources = sorted(expected_sources - present_sources)

    return LogGapAnalysisOut(
        sources=sources,
        detectable_stages=detectable,
        partial_stages=partial,
        blind_stages=blind,
        retention_gaps=retention_gaps,
        missing_sources=missing_sources,
    )
