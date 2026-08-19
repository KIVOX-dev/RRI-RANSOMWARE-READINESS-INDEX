from typing import Optional

from pydantic import BaseModel


class DomainComparison(BaseModel):
    domain: str
    organisation_score: float
    cohort_average: float


class BenchmarkOut(BaseModel):
    available: bool
    cohort_size: int
    sector: str
    maturity_percentile: Optional[float] = None
    assurance_comparison: Optional[float] = None
    domain_comparison: list[DomainComparison] = []
    cohort_distribution: list[float] = []
    message: str
    is_synthetic_cohort: bool = False


class TrendPoint(BaseModel):
    assessment_id: str
    completed_at: str
    maturity_score: float
    assurance_score: float


class TrendOut(BaseModel):
    available: bool
    points: list[TrendPoint] = []
    message: str
