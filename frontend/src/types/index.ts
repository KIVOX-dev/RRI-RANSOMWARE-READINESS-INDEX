export type UserRole = "org_user" | "org_admin" | "platform_admin";
export type Sector = "healthcare" | "education" | "local_government" | "finance" | "generic";
export type RoleName = "executive" | "it_administrator" | "generalist";
export type Language = "en" | "hi";
export type ImpactLevel = "low" | "medium" | "high";
export type AnswerType = "boolean" | "scale" | "single_select" | "multi_select" | "text";
export type AssessmentStatus = "draft" | "in_progress" | "completed";

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  organisation_id: string;
  language: Language;
  status: string;
}

export type OrganisationVerificationStatus = "pending" | "verified" | "rejected";

export interface Organisation {
  id: string;
  name: string;
  sector: string;
  size?: string;
  location?: string;
  is_synthetic: boolean;
  parent_organisation_id?: string;
  verification_status: OrganisationVerificationStatus;
}

export interface OrganisationDirectoryEntry {
  id: string;
  name: string;
}

export interface QuestionOption {
  value: string;
  label: string;
  score: number;
}

export interface MicroLearning {
  why_it_matters: string;
  risk_addressed: string;
  good_practice: string;
  evidence_hint: string;
}

export interface RegulatoryReference {
  framework: string;
  note: string;
  url?: string | null;
}

export interface RegulatoryContext {
  references: RegulatoryReference[];
  disclaimer: string;
}

export interface CisCdmSafeguard {
  id: string;
  title: string;
  ig: string;
  technique_count?: number;
}

export interface CisCdmReference {
  safeguards: CisCdmSafeguard[];
  note: string;
  source_title: string;
  source_url: string;
}

export interface Question {
  id: string;
  control_id: string;
  domain: string;
  title: string;
  description: string;
  answer_type: AnswerType;
  options: QuestionOption[];
  impact_level: ImpactLevel;
  weight: number;
  evidence_required: boolean;
  micro_learning?: MicroLearning;
  regulatory_context?: RegulatoryContext;
  cis_cdm_reference?: CisCdmReference;
  order: number;
  round: number;
  round_count: number;
}

export interface DomainScore {
  domain: string;
  maturity_score: number;
  assurance_score: number;
  control_count: number;
}

export interface HighImpactGap {
  control_id: string;
  title: string;
  domain: string;
  reason: string;
}

export type AssessmentMode = "basic" | "full";

export interface Assessment {
  id: string;
  organisation_id: string;
  created_by: string;
  sector: string;
  role: string;
  language: string;
  mode: AssessmentMode;
  status: AssessmentStatus;
  progress: number;
  started_at?: string;
  completed_at?: string;
  maturity_score?: number;
  assurance_score?: number;
  domain_scores: DomainScore[];
  high_impact_gaps: HighImpactGap[];
  total_controls: number;
  answered_controls: number;
}

export interface Answer {
  id: string;
  assessment_id: string;
  question_id: string;
  control_id: string;
  answer: unknown;
  score: number;
  weight: number;
  impact_level: string;
  answered_by: string;
  answered_at: string;
}

export interface Evidence {
  id: string;
  assessment_id: string;
  organisation_id: string;
  control_id: string;
  filename: string;
  object_key: string;
  mime_type: string;
  size: number;
  checksum: string;
  uploaded_by: string;
  verification_status: "pending" | "verified" | "rejected";
  created_at: string;
  download_url?: string;
}

export interface ProbeCheck {
  check_id: string;
  result: string;
  details?: Record<string, unknown>;
  timestamp: string;
  label?: string;
  control_id?: string;
}

export interface ProbeRun {
  id: string;
  assessment_id: string;
  organisation_id: string;
  host_fingerprint: string;
  timestamp: string;
  verification_status: string;
  checks: ProbeCheck[];
  created_at: string;
  note: string;
}

export type DetectionStatus = "covered" | "partial" | "blind";

export interface Requirement {
  key: string;
  description: string;
  met: boolean;
  basis: string;
  control_ids: string[];
}

export interface FrameworkCompliance {
  framework: string;
  verdict: "compliant" | "non_compliant";
  url?: string;
  requirements: Requirement[];
}

export interface RegulatoryCompliance {
  assessment_id: string;
  organisation_id: string;
  frameworks: FrameworkCompliance[];
  disclaimer: string;
}

export interface AttckTechnique {
  technique_id: string;
  name: string;
  mitre_tactics: string[];
  url: string;
}

export interface CisCdmBenchmark {
  tactic: string;
  coverage_pct: number;
  source: { title: string; publisher: string; url: string };
}

export interface DetectionStage {
  stage: string;
  status: DetectionStatus;
  supporting_controls: string[];
  evidence_status: string;
  log_coverage: number;
  explanation: string;
  attck_techniques: AttckTechnique[];
  cis_cdm_benchmark?: CisCdmBenchmark;
}

export interface LogSource {
  id?: string;
  assessment_id?: string;
  source_name: string;
  enabled: boolean;
  retention_days: number;
  monitored: boolean;
  covered_stages: string[];
  gaps?: string[];
}

export interface LogGapAnalysis {
  sources: LogSource[];
  detectable_stages: string[];
  partial_stages: string[];
  blind_stages: string[];
  retention_gaps: string[];
  missing_sources: string[];
}

export interface DwellTimeReadiness {
  score: number;
  credential_hygiene: number;
  password_reuse_signal: number;
  privilege_practices: number;
  lateral_movement_exposure: number;
  explanation: string;
}

export interface CanaryEvent {
  id: string;
  organisation_id: string;
  assessment_id?: string;
  canary_id: string;
  event_type: string;
  file_path: string;
  timestamp: string;
  severity: string;
  status: string;
  simulated: boolean;
}

export interface Canary {
  id: string;
  canary_id: string;
  organisation_id: string;
  assessment_id?: string;
  file_path: string;
  status: string;
}

export type RemediationPriority = "critical" | "high" | "medium" | "low";
export type EffortLevel = "low" | "high";

export interface RemediationItem {
  id: string;
  assessment_id: string;
  control_id: string;
  issue: string;
  domain: string;
  impact: ImpactLevel;
  effort: EffortLevel;
  priority: RemediationPriority;
  reason: string;
  recommended_action: string;
  status: string;
}

export interface Report {
  id: string;
  assessment_id: string;
  organisation_id: string;
  report_type: string;
  version: number;
  object_key: string;
  checksum: string;
  generated_at: string;
  status: string;
  download_url?: string;
}

export interface DomainComparison {
  domain: string;
  organisation_score: number;
  cohort_average: number;
}

export interface Benchmark {
  available: boolean;
  cohort_size: number;
  sector: string;
  maturity_percentile?: number;
  assurance_comparison?: number;
  domain_comparison: DomainComparison[];
  cohort_distribution: number[];
  message: string;
  is_synthetic_cohort: boolean;
}

export interface TrendPoint {
  assessment_id: string;
  completed_at: string;
  maturity_score: number;
  assurance_score: number;
}

export interface Trend {
  available: boolean;
  points: TrendPoint[];
  message: string;
}

export interface LedgerEntry {
  id: string;
  organisation_id: string;
  organisation_name: string;
  sequence: number;
  assessment_id?: string;
  report_id?: string;
  timestamp: string;
  payload_hash: string;
  previous_record_hash: string;
  record_hash: string;
  signature: string;
  fabric_anchor?: string;
  verification_status: string;
  record_type: string;
  sub_organisation_id?: string;
}

export interface LedgerVerifyResult {
  verified: boolean;
  total_records: number;
  broken_at_sequence?: number;
  message: string;
}

export interface FabricStatus {
  enabled: boolean;
  connected: boolean;
  anchor_count: number | null;
  contract_address: string | null;
}

export interface AdminOrganisation extends Organisation {
  assessment_status: string;
  maturity_score?: number;
  assurance_score?: number;
  completion_date?: string;
  total_assessments: number;
}

export interface BackupResilience {
  id?: string;
  assessment_id: string;
  organisation_id: string;
  backup_destination: string;
  is_writable_from_production: boolean;
  backup_frequency: string;
  last_successful_backup?: string;
  last_restore_test?: string;
  restore_test_owner?: string;
  recovery_confidence: number;
  restore_test_gap: boolean;
  risk_note: string;
}

export interface DashboardData {
  assessment: Assessment;
  detection_matrix: DetectionStage[];
  dwell_time_readiness: DwellTimeReadiness;
  evidence_count: number;
  probe_status: string;
}
