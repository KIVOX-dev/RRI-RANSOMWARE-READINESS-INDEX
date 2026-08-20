"""A2 — Weighted Scoring Engine.

Computes Maturity (0-5) and Assurance (0-100%) purely from stored answers,
evidence and probe results, using weights/rules read from the active
scoring_configs document. Never accepts a client-submitted score. Always
called server-side after an answer is submitted, evidence is uploaded, or a
probe run is ingested, and its output is the only thing ever persisted to
assessment.maturity_score / assessment.assurance_score.
"""
from app.models.assessment import DomainScore, HighImpactGap
from app.repositories.collections import (
    answers_repo,
    assessments_repo,
    evidence_repo,
    probe_checks_repo,
    probe_runs_repo,
    questions_repo,
    scoring_configs_repo,
)

IMPACT_ORDER = {"low": 0, "medium": 1, "high": 2}


def get_active_scoring_config() -> dict:
    config = scoring_configs_repo.find_one({"active": True})
    if config:
        return config
    return {
        "impact_multipliers": {"low": 1.0, "medium": 1.5, "high": 2.0},
        "assurance_rules": {
            "unverified_claim_weight": 0.35,
            "evidence_weight": 0.75,
            "evidence_verified_weight": 0.9,
            "probe_verified_weight": 1.0,
            "high_impact_assurance_threshold": 0.6,
        },
    }


def _evidence_assurance_fraction(evidence_docs: list[dict], rules: dict) -> float:
    if not evidence_docs:
        return 0.0
    best = 0.0
    for ev in evidence_docs:
        if ev.get("verification_status") == "verified":
            best = max(best, rules["evidence_verified_weight"])
        else:
            best = max(best, rules["evidence_weight"])
    return best


def _probe_assurance_fraction(control_id: str, probe_checks_by_control: dict, rules: dict) -> float:
    check = probe_checks_by_control.get(control_id)
    if not check:
        return 0.0
    if check.get("result") == "pass":
        return rules["probe_verified_weight"]
    return 0.0


def recompute_assessment_scores(assessment_id: str) -> dict:
    assessment = assessments_repo.get_by_id(assessment_id)
    if not assessment:
        raise ValueError("Assessment not found")

    config = get_active_scoring_config()
    impact_multipliers = config["impact_multipliers"]
    rules = config["assurance_rules"]

    # Must mirror routing_service.get_routed_questions' query exactly: Basic
    # mode is a fixed, role-agnostic control subset (basic_track=True), not
    # the normal role filter applied to fewer controls. Using the role filter
    # here for basic-mode assessments would silently drop answers to any
    # basic-track control tagged technical-role-only (about half of them),
    # understating scores for non-technical roles despite every question
    # having been answered.
    scoring_query = {
        "active": True,
        "sector": {"$in": [assessment["sector"], "generic"]},
    }
    if assessment.get("mode") == "basic":
        scoring_query["basic_track"] = True
    else:
        scoring_query["roles"] = assessment["role"]
    relevant_questions = questions_repo.find(scoring_query)
    total_controls = len(relevant_questions)

    answers = answers_repo.find({"assessment_id": assessment_id})
    answers_by_control = {a["control_id"]: a for a in answers}

    evidence_docs = evidence_repo.find({"assessment_id": assessment_id})
    evidence_by_control: dict[str, list[dict]] = {}
    for ev in evidence_docs:
        evidence_by_control.setdefault(ev["control_id"], []).append(ev)

    latest_probe_run = None
    probe_runs = probe_runs_repo.find(
        {"assessment_id": assessment_id, "verification_status": "verified"}, sort=[("created_at", -1)], limit=1
    )
    probe_checks_by_control: dict[str, dict] = {}
    if probe_runs:
        latest_probe_run = probe_runs[0]
        checks = probe_checks_repo.find({"probe_run_id": latest_probe_run["id"]})
        questions_by_probe_check = {
            q.get("probe_check_id"): q["control_id"] for q in relevant_questions if q.get("probe_check_id")
        }
        for check in checks:
            control_id = questions_by_probe_check.get(check["check_id"])
            if control_id:
                probe_checks_by_control[control_id] = check

    domain_accumulator: dict[str, dict] = {}
    high_impact_gaps: list[HighImpactGap] = []
    overall_weighted_maturity = 0.0
    overall_weighted_assurance = 0.0
    overall_weight_sum = 0.0
    answered_controls = 0

    questions_by_control = {q["control_id"]: q for q in relevant_questions}

    for control_id, answer in answers_by_control.items():
        question = questions_by_control.get(control_id)
        if not question:
            continue
        answered_controls += 1
        weight = float(answer.get("weight", question.get("weight", 1.0)))
        impact_level = answer.get("impact_level", question.get("impact_level", "medium"))
        effective_weight = weight * impact_multipliers.get(impact_level, 1.0)
        score = float(answer.get("score", 0.0))

        evidence_fraction = _evidence_assurance_fraction(evidence_by_control.get(control_id, []), rules)
        probe_fraction = _probe_assurance_fraction(control_id, probe_checks_by_control, rules)
        base_fraction = rules["unverified_claim_weight"] if score > 0 else 0.0
        assurance_fraction = max(base_fraction, evidence_fraction, probe_fraction)

        domain = question.get("domain", "General")
        bucket = domain_accumulator.setdefault(
            domain, {"maturity_weighted": 0.0, "assurance_weighted": 0.0, "weight_sum": 0.0, "count": 0}
        )
        bucket["maturity_weighted"] += score * effective_weight
        bucket["assurance_weighted"] += assurance_fraction * effective_weight
        bucket["weight_sum"] += effective_weight
        bucket["count"] += 1

        overall_weighted_maturity += score * effective_weight
        overall_weighted_assurance += assurance_fraction * effective_weight
        overall_weight_sum += effective_weight

        if impact_level == "high" and assurance_fraction < rules["high_impact_assurance_threshold"]:
            question_title = question.get("title", {})
            title_text = question_title.get("en", control_id) if isinstance(question_title, dict) else str(question_title)
            high_impact_gaps.append(
                HighImpactGap(
                    control_id=control_id,
                    title=title_text,
                    domain=domain,
                    reason=(
                        "High-impact control claimed but not sufficiently supported by evidence or "
                        "verification probe results."
                    ),
                )
            )

    domain_scores = [
        DomainScore(
            domain=domain,
            maturity_score=round(bucket["maturity_weighted"] / bucket["weight_sum"], 2) if bucket["weight_sum"] else 0.0,
            assurance_score=round((bucket["assurance_weighted"] / bucket["weight_sum"]) * 100, 1) if bucket["weight_sum"] else 0.0,
            control_count=bucket["count"],
        )
        for domain, bucket in sorted(domain_accumulator.items())
    ]

    maturity_score = round(overall_weighted_maturity / overall_weight_sum, 2) if overall_weight_sum else 0.0
    assurance_score = round((overall_weighted_assurance / overall_weight_sum) * 100, 1) if overall_weight_sum else 0.0
    progress = round((answered_controls / total_controls) * 100, 1) if total_controls else 0.0

    update = {
        "maturity_score": min(5.0, max(0.0, maturity_score)),
        "assurance_score": min(100.0, max(0.0, assurance_score)),
        "domain_scores": [d.model_dump() for d in domain_scores],
        "high_impact_gaps": [g.model_dump() for g in high_impact_gaps],
        "progress": progress,
        "answered_controls": answered_controls,
        "total_controls": total_controls,
    }
    assessments_repo.update_by_id(assessment_id, update)
    return update
