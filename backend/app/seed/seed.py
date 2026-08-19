"""Idempotent seed script — run at container startup (see docker-compose.yml).
Populates the question bank, sectors, roles, active scoring config, and a set
of clearly-labeled synthetic organisations/assessments so benchmarking and
trend analytics have real (if seeded) data to compute over."""
import random
from datetime import datetime, timedelta, timezone

from app.core.mongo import ensure_indexes, get_db
from app.core.security import hash_password
from app.seed.questions_data import (
    BASIC_TRACK_CONTROL_IDS,
    CIS_CDM_REFERENCE,
    DOMAIN_CONTROLS,
    DOMAIN_MICRO_LEARNING_EN,
    DOMAIN_MICRO_LEARNING_HI,
    INDIAN_REGULATORY_CONTEXT,
)

SECTORS = [
    {"key": "healthcare", "name_en": "Healthcare", "name_hi": "स्वास्थ्य सेवा"},
    {"key": "education", "name_en": "Education", "name_hi": "शिक्षा"},
    {"key": "local_government", "name_en": "Local Government", "name_hi": "स्थानीय सरकार"},
    {"key": "finance", "name_en": "Finance", "name_hi": "वित्त"},
    {"key": "generic", "name_en": "Generic / Other", "name_hi": "सामान्य / अन्य"},
]

ROLES = [
    {"key": "executive", "name_en": "Executive", "name_hi": "कार्यकारी"},
    {"key": "it_administrator", "name_en": "IT Administrator", "name_hi": "आईटी व्यवस्थापक"},
    {"key": "generalist", "name_en": "Generalist", "name_hi": "सामान्यवादी"},
]

SYNTHETIC_ORGS = [
    {"name": "Sample Northgate Hospital", "sector": "healthcare", "size": "500-1000 staff", "location": "Sample City, IN"},
    {"name": "Sample Riverside Health Group", "sector": "healthcare", "size": "1000+ staff", "location": "Sample City, IN"},
    {"name": "Sample Lakeside Clinic Network", "sector": "healthcare", "size": "100-500 staff", "location": "Sample Town, IN"},
    {"name": "Sample Cedar Valley Medical Center", "sector": "healthcare", "size": "500-1000 staff", "location": "Sample City, IN"},
    {"name": "Sample Union School District", "sector": "education", "size": "500-1000 staff", "location": "Sample County, IN"},
    {"name": "Sample Metro Community College", "sector": "education", "size": "100-500 staff", "location": "Sample City, IN"},
    {"name": "Sample Township of Millbrook", "sector": "local_government", "size": "100-500 staff", "location": "Millbrook, IN"},
    {"name": "Sample County Records Office", "sector": "local_government", "size": "<100 staff", "location": "Sample County, IN"},
    {"name": "Sample Trustline Credit Union", "sector": "finance", "size": "100-500 staff", "location": "Sample City, IN"},
    {"name": "Sample Harbor Community Bank", "sample": True, "sector": "finance", "size": "500-1000 staff", "location": "Sample City, IN"},
]


def build_question_documents() -> list[dict]:
    docs = []
    order = 0
    for domain, controls in DOMAIN_CONTROLS.items():
        micro_en = DOMAIN_MICRO_LEARNING_EN[domain]
        micro_hi = DOMAIN_MICRO_LEARNING_HI[domain]
        for (
            control_id, title_en, title_hi, desc_en, desc_hi, impact, answer_type,
            weight, evidence_required, options, probe_check_id, sector, roles,
        ) in controls:
            order += 1
            opts = None
            if options:
                opts = [
                    {"value": v, "label": {"en": label_en, "hi": label_hi}, "score": score}
                    for (v, label_en, label_hi, score) in options
                ]
            regulatory_refs = INDIAN_REGULATORY_CONTEXT.get(control_id)
            cis_cdm = CIS_CDM_REFERENCE.get(control_id)
            docs.append(
                {
                    "control_id": control_id,
                    "title": {"en": title_en, "hi": title_hi},
                    "description": {"en": desc_en, "hi": desc_hi},
                    "domain": domain,
                    "sector": sector,
                    "roles": roles,
                    "answer_type": answer_type,
                    "options": opts or [],
                    "weight": weight,
                    "impact_level": impact,
                    "branching_rules": {},
                    "micro_learning": {"en": micro_en, "hi": micro_hi},
                    "regulatory_context": {"references": regulatory_refs} if regulatory_refs else None,
                    "cis_cdm_reference": cis_cdm,
                    "basic_track": control_id in BASIC_TRACK_CONTROL_IDS,
                    "evidence_required": evidence_required,
                    "probe_check_id": probe_check_id,
                    "active": True,
                    "order": order,
                }
            )
    return docs


def seed_reference_data(db) -> None:
    if db.sectors.count_documents({}) == 0:
        db.sectors.insert_many(SECTORS)
    if db.roles.count_documents({}) == 0:
        db.roles.insert_many(ROLES)


def seed_questions(db) -> None:
    docs = build_question_documents()
    for doc in docs:
        db.questions.update_one({"control_id": doc["control_id"]}, {"$set": doc}, upsert=True)
    print(f"Seeded {len(docs)} questions across {len(DOMAIN_CONTROLS)} domains.")


def seed_scoring_config(db) -> None:
    if db.scoring_configs.count_documents({"active": True}) > 0:
        return
    db.scoring_configs.insert_one(
        {
            "version": 1,
            "domains": list(DOMAIN_CONTROLS.keys()),
            "impact_multipliers": {"low": 1.0, "medium": 1.5, "high": 2.0},
            "assurance_rules": {
                "unverified_claim_weight": 0.35,
                "evidence_weight": 0.75,
                "evidence_verified_weight": 0.9,
                "probe_verified_weight": 1.0,
                "high_impact_assurance_threshold": 0.6,
            },
            "active": True,
            "created_at": datetime.now(timezone.utc),
        }
    )
    print("Seeded active scoring config.")


def _random_answer(question: dict) -> tuple:
    """Returns (answer_value, score) biased toward a plausible maturity spread."""
    answer_type = question["answer_type"]
    if answer_type == "boolean":
        value = random.random() < 0.62
        return value, (5.0 if value else 0.0)
    if answer_type == "scale":
        score = round(random.uniform(1.5, 5.0), 1)
        return score, score
    if answer_type == "select":
        opt = random.choices(question["options"], weights=[1, 2, 3, 3, 2])[0] if len(question["options"]) == 5 else random.choice(question["options"])
        return opt["value"], float(opt["score"])
    return "yes", 3.0


def seed_synthetic_organisations_and_assessments(db) -> None:
    if db.organisations.count_documents({"is_synthetic": True}) > 0:
        return

    all_questions = list(db.questions.find({"active": True}))

    for org_data in SYNTHETIC_ORGS:
        org_id = db.organisations.insert_one(
            {
                "name": org_data["name"],
                "sector": org_data["sector"],
                "size": org_data["size"],
                "location": org_data["location"],
                "is_synthetic": True,
                "created_at": datetime.now(timezone.utc),
            }
        ).inserted_id

        admin_email = org_data["name"].lower().replace(" ", ".").replace("sample.", "") + "@sample-demo.rri"
        user_id = db.users.insert_one(
            {
                "organisation_id": str(org_id),
                "name": "Demo Admin",
                "email": admin_email,
                "password_hash": hash_password("SampleDemo123!"),
                "role": "org_admin",
                "language": "en",
                "status": "active",
                "created_at": datetime.now(timezone.utc),
            }
        ).inserted_id

        # 1-3 historical completed assessments per synthetic org for trend/benchmark demo data
        num_history = random.choice([1, 2, 3])
        role = random.choice(["executive", "it_administrator", "generalist"])
        relevant_questions = [
            q for q in all_questions
            if q["sector"] in (org_data["sector"], "generic") and role in q["roles"]
        ]

        base_time = datetime.now(timezone.utc) - timedelta(days=30 * num_history)
        for i in range(num_history):
            completed_at = base_time + timedelta(days=30 * i)
            assessment_id = db.assessments.insert_one(
                {
                    "organisation_id": str(org_id),
                    "created_by": str(user_id),
                    "sector": org_data["sector"],
                    "role": role,
                    "language": "en",
                    "mode": "full",
                    "status": "completed",
                    "progress": 100.0,
                    "started_at": completed_at - timedelta(days=5),
                    "completed_at": completed_at,
                    "maturity_score": 0,
                    "assurance_score": 0,
                    "domain_scores": [],
                    "high_impact_gaps": [],
                    "total_controls": len(relevant_questions),
                    "answered_controls": 0,
                    "created_at": completed_at - timedelta(days=5),
                }
            ).inserted_id

            domain_scores_acc: dict[str, list[float]] = {}
            total_score = 0.0
            answered = 0
            improvement_bias = i * 0.3  # later assessments trend slightly better
            for q in relevant_questions:
                value, score = _random_answer(q)
                score = min(5.0, score + improvement_bias) if isinstance(score, float) else score
                db.answers.insert_one(
                    {
                        "assessment_id": str(assessment_id),
                        "question_id": str(q["_id"]),
                        "control_id": q["control_id"],
                        "answer": value,
                        "score": score,
                        "weight": q["weight"],
                        "impact_level": q["impact_level"],
                        "answered_by": str(user_id),
                        "answered_at": completed_at - timedelta(days=4),
                    }
                )
                domain_scores_acc.setdefault(q["domain"], []).append(score)
                total_score += score
                answered += 1

            domain_scores = [
                {"domain": d, "maturity_score": round(sum(v) / len(v), 2), "assurance_score": round(random.uniform(35, 85), 1), "control_count": len(v)}
                for d, v in domain_scores_acc.items()
            ]
            maturity = round(total_score / answered, 2) if answered else 0.0
            assurance = round(random.uniform(40, 80) + improvement_bias * 5, 1)

            db.assessments.update_one(
                {"_id": assessment_id},
                {
                    "$set": {
                        "maturity_score": min(5.0, maturity),
                        "assurance_score": min(100.0, assurance),
                        "domain_scores": domain_scores,
                        "answered_controls": answered,
                    }
                },
            )

    print(f"Seeded {len(SYNTHETIC_ORGS)} synthetic organisations with historical assessments.")


def run() -> None:
    db = get_db()
    ensure_indexes()
    seed_reference_data(db)
    seed_questions(db)
    seed_scoring_config(db)
    seed_synthetic_organisations_and_assessments(db)
    print("Seed complete.")


if __name__ == "__main__":
    run()
