"""D2 — Remediation Roadmap. Every item is derived from an actual assessment
gap (a control scored below full marks, or a high-impact control flagged as
unverified) — nothing here is templated independently of stored answers."""
from app.repositories.collections import answers_repo, assessments_repo, questions_repo, remediation_items_repo

HIGH_EFFORT_DOMAINS = {
    "Network Segmentation", "Backup & Recovery", "Endpoint & AV/EDR",
    "Logging & Monitoring", "Patch & Vulnerability Management", "Identity & Access Management",
    "Data Protection",
}


def _effort_for_domain(domain: str) -> str:
    return "high" if domain in HIGH_EFFORT_DOMAINS else "low"


def _priority(impact_level: str, score: float, is_high_impact_gap: bool) -> str:
    if impact_level == "high" and (score == 0 or is_high_impact_gap):
        return "critical"
    if impact_level == "high" and score < 3:
        return "high"
    if impact_level == "medium" and score < 2:
        return "high"
    if score < 3:
        return "medium"
    return "low"


def generate_remediation_items(assessment_id: str) -> list[dict]:
    assessment = assessments_repo.get_by_id(assessment_id)
    if not assessment:
        raise ValueError("Assessment not found")

    high_impact_gap_controls = {g["control_id"] for g in assessment.get("high_impact_gaps", [])}
    answers = answers_repo.find({"assessment_id": assessment_id})
    questions_by_control = {q["control_id"]: q for q in questions_repo.find({})}

    for existing in remediation_items_repo.find({"assessment_id": assessment_id}):
        remediation_items_repo.delete_by_id(existing["id"])

    items = []
    for answer in answers:
        question = questions_by_control.get(answer["control_id"])
        if not question:
            continue
        score = float(answer.get("score", 0))
        is_gap = answer["control_id"] in high_impact_gap_controls
        if score >= 4.5 and not is_gap:
            continue  # control is well-implemented and sufficiently assured — no remediation needed

        domain = question["domain"]
        impact = question["impact_level"]
        effort = _effort_for_domain(domain)
        priority = _priority(impact, score, is_gap)

        good_practice = None
        for lang_block in (question.get("micro_learning") or {}).values():
            good_practice = lang_block.get("good_practice")
            break

        if score == 0:
            issue = f"{question['title'].get('en', answer['control_id'])} is not implemented."
            reason = f"Control answered negatively; impact level is {impact}."
        elif is_gap:
            issue = f"{question['title'].get('en', answer['control_id'])} is claimed but not sufficiently evidenced or verified."
            reason = "High-impact control lacks supporting evidence or a passing verification probe result."
        else:
            issue = f"{question['title'].get('en', answer['control_id'])} is only partially implemented."
            reason = f"Answer score {score}/5 indicates partial maturity for a {impact}-impact control."

        doc = {
            "assessment_id": assessment_id,
            "control_id": answer["control_id"],
            "issue": issue,
            "domain": domain,
            "impact": impact,
            "effort": effort,
            "priority": priority,
            "reason": reason,
            "recommended_action": good_practice or f"Review and strengthen the control: {question['title'].get('en', '')}",
            "status": "open",
        }
        item_id = remediation_items_repo.insert(doc)
        items.append(remediation_items_repo.get_by_id(item_id))

    priority_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    items.sort(key=lambda i: priority_rank.get(i["priority"], 4))
    return items


def list_remediation_items(assessment_id: str, domain: str | None = None, impact: str | None = None,
                            effort: str | None = None, priority: str | None = None) -> list[dict]:
    items = remediation_items_repo.find({"assessment_id": assessment_id})
    if domain:
        items = [i for i in items if i["domain"] == domain]
    if impact:
        items = [i for i in items if i["impact"] == impact]
    if effort:
        items = [i for i in items if i["effort"] == effort]
    if priority:
        items = [i for i in items if i["priority"] == priority]
    priority_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    items.sort(key=lambda i: priority_rank.get(i["priority"], 4))
    return items
