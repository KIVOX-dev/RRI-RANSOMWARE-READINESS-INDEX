"""Real MITRE ATT&CK Enterprise CTI, curated for this platform's 5-stage
ransomware kill-chain model. Data was pulled from the official STIX 2.1
bundle (github.com/mitre-attack/attack-stix-data) rather than hand-authored,
and every technique_id was checked against the current dataset's
`revoked`/`revoked-by` relationships — a cited-but-revoked ID (T1562) was
traced to its real current replacement (T1685) rather than shipped stale.
See app/seed/attck_techniques.json for provenance metadata and the full set.
"""
import json
from functools import lru_cache
from pathlib import Path

from app.models.detection import AttckTechniqueOut

_DATA_PATH = Path(__file__).resolve().parent.parent / "seed" / "attck_techniques.json"


@lru_cache(maxsize=1)
def _load() -> dict:
    with open(_DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_meta() -> dict:
    return _load()["meta"]


def get_all_techniques() -> dict[str, dict]:
    return _load()["techniques"]


@lru_cache(maxsize=1)
def get_techniques_by_stage() -> dict[str, list[AttckTechniqueOut]]:
    by_stage: dict[str, list[AttckTechniqueOut]] = {}
    for tech in get_all_techniques().values():
        by_stage.setdefault(tech["stage"], []).append(
            AttckTechniqueOut(
                technique_id=tech["technique_id"],
                name=tech["name"],
                mitre_tactics=tech["mitre_tactics"],
                url=tech["url"],
            )
        )
    return by_stage


def techniques_for_stage(stage: str) -> list[AttckTechniqueOut]:
    return get_techniques_by_stage().get(stage, [])
