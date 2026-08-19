"""Indian regulatory awareness — informational only, not a compliance
verdict. Surfaces the curated, control-linked references from
app/seed/questions_data.py as a deduplicated summary for reports and the
compliance domain, independent of how the organisation actually answered
those controls (the obligations apply regardless of self-reported maturity).
"""
from app.seed.questions_data import INDIAN_REGULATORY_CONTEXT

DISCLAIMER = (
    "Informational awareness only, not legal advice, and not a compliance certification. "
    "Applicability depends on your organisation's specific sector, scale, and data processed — "
    "confirm current obligations with qualified legal/compliance counsel."
)


def get_regulatory_summary() -> list[dict]:
    """Every distinct (framework, note) pair cited anywhere in the question
    bank, in first-seen order — a flat list suitable for a report section."""
    seen: set[tuple[str, str]] = set()
    summary: list[dict] = []
    for refs in INDIAN_REGULATORY_CONTEXT.values():
        for ref in refs:
            key = (ref["framework"], ref["note"])
            if key in seen:
                continue
            seen.add(key)
            summary.append(ref)
    return summary
