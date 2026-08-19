"""C1 — Role + Sector Routing. Determines which questions are visible for a
given assessment's sector/role/language selection."""
from app.models.question import CisCdmReference, MicroLearning, QuestionOption, QuestionOut, RegulatoryContext
from app.repositories.collections import questions_repo

ROUND_SIZE = 25
IMPACT_SORT_RANK = {"high": 0, "medium": 1, "low": 2}


def get_routed_questions(sector: str, role: str, language: str = "en", mode: str = "full") -> list[QuestionOut]:
    query = {"active": True, "sector": {"$in": [sector, "generic"]}}
    if mode == "basic":
        # Basic mode is a genuinely distinct track, not just the same role
        # filter applied to fewer controls: it's a fixed, hand-curated
        # ~23-control subset (see BASIC_TRACK_CONTROL_IDS) chosen for
        # plain-language phrasing regardless of role, so an executive and an
        # IT administrator both get the same short, jargon-light flow. The
        # normal role filter is deliberately skipped here — about half the
        # curated controls are tagged technical-role-only for the full
        # track, which would otherwise silently gut the basic set for
        # non-technical roles.
        query["basic_track"] = True
    else:
        query["roles"] = role
    docs = questions_repo.find(query, sort=[("order", 1)])
    # Impact-first ordering: within each round, the most consequential
    # controls come first. `sort` is stable, so ties keep their original
    # domain-grouped order from the query above.
    docs.sort(key=lambda d: IMPACT_SORT_RANK.get(d.get("impact_level"), 3))

    total = len(docs)
    round_count = max(1, -(-total // ROUND_SIZE))  # ceil division

    out = []
    for index, doc in enumerate(docs):
        title = doc.get("title", {}).get(language) or doc.get("title", {}).get("en", "")
        description = doc.get("description", {}).get(language) or doc.get("description", {}).get("en", "")
        micro = doc.get("micro_learning")
        micro_out = None
        if micro:
            localized = micro.get(language) or micro.get("en")
            if localized:
                micro_out = MicroLearning(**localized)
        options = [
            QuestionOption(value=o["value"], label=o.get("label", {}).get(language) or o.get("label", {}).get("en", o["value"]), score=o["score"])
            for o in doc.get("options", [])
        ]
        regulatory_context = doc.get("regulatory_context")
        regulatory_out = RegulatoryContext(**regulatory_context) if regulatory_context else None
        cis_cdm = doc.get("cis_cdm_reference")
        cis_cdm_out = CisCdmReference(**cis_cdm) if cis_cdm else None
        out.append(
            QuestionOut(
                id=doc["id"],
                control_id=doc["control_id"],
                domain=doc["domain"],
                title=title,
                description=description,
                answer_type=doc["answer_type"],
                options=options,
                impact_level=doc["impact_level"],
                weight=doc["weight"],
                evidence_required=doc.get("evidence_required", False),
                micro_learning=micro_out,
                regulatory_context=regulatory_out,
                cis_cdm_reference=cis_cdm_out,
                basic_track=doc.get("basic_track", False),
                order=doc.get("order", 0),
                round=(index // ROUND_SIZE) + 1,
                round_count=round_count,
            )
        )
    return out


def score_answer(question_doc: dict, answer_value) -> float:
    answer_type = question_doc["answer_type"]
    if answer_type == "boolean":
        return 5.0 if answer_value is True else 0.0
    if answer_type == "scale":
        try:
            value = float(answer_value)
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, min(5.0, value))
    if answer_type in ("single_select",):
        for opt in question_doc.get("options", []):
            if opt["value"] == answer_value:
                return float(opt["score"])
        return 0.0
    if answer_type == "multi_select":
        if not isinstance(answer_value, list) or not answer_value:
            return 0.0
        scores = [float(o["score"]) for o in question_doc.get("options", []) if o["value"] in answer_value]
        return round(sum(scores) / len(scores), 2) if scores else 0.0
    if answer_type == "text":
        return 5.0 if isinstance(answer_value, str) and answer_value.strip() else 0.0
    return 0.0
