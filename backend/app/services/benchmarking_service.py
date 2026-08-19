"""D4 — Sector Benchmarking. Cohorts below 5 distinct organisations never
render numbers — an explicit empty state is returned instead."""
import statistics

from app.models.benchmarking import BenchmarkOut, DomainComparison
from app.repositories.collections import assessments_repo, organisations_repo

MIN_COHORT_SIZE = 5


def get_benchmark(organisation_id: str) -> BenchmarkOut:
    org = organisations_repo.get_by_id(organisation_id)
    if not org:
        raise ValueError("Organisation not found")

    my_latest = assessments_repo.find(
        {"organisation_id": organisation_id, "status": "completed"}, sort=[("completed_at", -1)], limit=1
    )
    if not my_latest:
        return BenchmarkOut(
            available=False, cohort_size=0, sector=org["sector"],
            message="Complete an assessment for this organisation before viewing sector benchmarking.",
        )

    sector_completed = assessments_repo.find({"sector": org["sector"], "status": "completed"})
    cohort_org_ids = {a["organisation_id"] for a in sector_completed} - {organisation_id}

    if len(cohort_org_ids) < MIN_COHORT_SIZE:
        return BenchmarkOut(
            available=False, cohort_size=len(cohort_org_ids), sector=org["sector"],
            message=(
                f"Sector cohort for '{org['sector']}' currently has {len(cohort_org_ids)} other organisation(s) "
                f"with a completed assessment — at least {MIN_COHORT_SIZE} are required before benchmark "
                "numbers can be shown."
            ),
        )

    cohort_latest = []
    for oid in cohort_org_ids:
        latest = assessments_repo.find({"organisation_id": oid, "status": "completed"}, sort=[("completed_at", -1)], limit=1)
        if latest:
            cohort_latest.append(latest[0])

    cohort_orgs = organisations_repo.find({})
    synthetic_ids = {o["id"] for o in cohort_orgs if o.get("is_synthetic")}
    is_synthetic_cohort = bool(cohort_org_ids & synthetic_ids)

    my_maturity = my_latest[0]["maturity_score"] or 0
    my_assurance = my_latest[0]["assurance_score"] or 0
    cohort_maturities = [a["maturity_score"] or 0 for a in cohort_latest]
    cohort_assurances = [a["assurance_score"] or 0 for a in cohort_latest]

    percentile = round((sum(1 for m in cohort_maturities if m <= my_maturity) / len(cohort_maturities)) * 100, 1)
    assurance_comparison = round(my_assurance - statistics.mean(cohort_assurances), 1)

    my_domain_scores = {d["domain"]: d["maturity_score"] for d in my_latest[0].get("domain_scores", [])}
    cohort_domain_values: dict[str, list[float]] = {}
    for a in cohort_latest:
        for d in a.get("domain_scores", []):
            cohort_domain_values.setdefault(d["domain"], []).append(d["maturity_score"])

    domain_comparison = [
        DomainComparison(
            domain=domain,
            organisation_score=my_score,
            cohort_average=round(statistics.mean(cohort_domain_values.get(domain, [0])), 2) if cohort_domain_values.get(domain) else 0.0,
        )
        for domain, my_score in my_domain_scores.items()
    ]

    return BenchmarkOut(
        available=True,
        cohort_size=len(cohort_org_ids),
        sector=org["sector"],
        maturity_percentile=percentile,
        assurance_comparison=assurance_comparison,
        domain_comparison=domain_comparison,
        cohort_distribution=sorted(cohort_maturities),
        message="Sample/Synthetic Data included in this cohort." if is_synthetic_cohort else "Benchmark computed from real completed assessments in this sector.",
        is_synthetic_cohort=is_synthetic_cohort,
    )
