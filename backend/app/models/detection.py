from typing import Optional

from pydantic import BaseModel

from app.models.common import DetectionStatus


class AttckTechniqueOut(BaseModel):
    technique_id: str
    name: str
    mitre_tactics: list[str] = []
    url: str


class CisCdmBenchmarkOut(BaseModel):
    tactic: str
    coverage_pct: float
    source: dict


class DetectionStageOut(BaseModel):
    stage: str
    status: DetectionStatus
    supporting_controls: list[str] = []
    evidence_status: str
    log_coverage: float = 0.0
    explanation: str
    attck_techniques: list[AttckTechniqueOut] = []
    cis_cdm_benchmark: Optional[CisCdmBenchmarkOut] = None


class LogSourceIn(BaseModel):
    source_name: str
    enabled: bool
    retention_days: int = 0
    monitored: bool = False
    covered_stages: list[str] = []


class LogSourceOut(LogSourceIn):
    id: str
    assessment_id: str
    gaps: list[str] = []


class LogGapAnalysisOut(BaseModel):
    sources: list[LogSourceOut]
    detectable_stages: list[str]
    partial_stages: list[str]
    blind_stages: list[str]
    retention_gaps: list[str]
    missing_sources: list[str]


class DwellTimeReadinessOut(BaseModel):
    score: float
    credential_hygiene: float
    password_reuse_signal: float
    privilege_practices: float
    lateral_movement_exposure: float
    explanation: str
