import { api } from "@/lib/api";
import type {
  Assessment, Answer, AdminOrganisation, BackupResilience, Benchmark, Canary, CanaryEvent,
  DashboardData, DetectionStage, DwellTimeReadiness, Evidence, FabricStatus, LedgerEntry, LedgerVerifyResult,
  LogGapAnalysis, LogSource, Organisation, OrganisationDirectoryEntry, ProbeRun, Question, RegulatoryCompliance,
  RemediationItem, Report, Trend, User,
} from "@/types";

// ---- Auth ----
export const AuthAPI = {
  register: (payload: { name: string; email: string; password: string; organisation: { name: string; sector: string; size?: string; location?: string; parent_organisation_id?: string }; language: string }) =>
    api.post("/auth/register", payload).then((r) => r.data),
  login: (payload: { email: string; password: string }) => api.post("/auth/login", payload).then((r) => r.data),
  me: () => api.get<User>("/auth/me").then((r) => r.data),
};

// ---- Organisations ----
export const OrgAPI = {
  me: () => api.get<Organisation>("/organisations/me").then((r) => r.data),
  get: (id: string) => api.get<Organisation>(`/organisations/${id}`).then((r) => r.data),
  directory: () => api.get<OrganisationDirectoryEntry[]>("/organisations/directory").then((r) => r.data),
};

// ---- Questions ----
export const QuestionsAPI = {
  list: (sector: string, role: string, language = "en", mode: "basic" | "full" = "full") =>
    api.get<Question[]>("/questions", { params: { sector, role, language, mode } }).then((r) => r.data),
};

// ---- Assessments ----
export const AssessmentsAPI = {
  start: (payload: { sector: string; role: string; language: string; mode: "basic" | "full" }) =>
    api.post<Assessment>("/assessments/start", payload).then((r) => r.data),
  list: () => api.get<Assessment[]>("/assessments").then((r) => r.data),
  get: (id: string) => api.get<Assessment>(`/assessments/${id}`).then((r) => r.data),
  submitAnswer: (id: string, control_id: string, answer: unknown) =>
    api.post<Answer>(`/assessments/${id}/answers`, { control_id, answer }).then((r) => r.data),
  listAnswers: (id: string) => api.get<Answer[]>(`/assessments/${id}/answers`).then((r) => r.data),
  complete: (id: string) => api.post<Assessment>(`/assessments/${id}/complete`).then((r) => r.data),
};

// ---- Evidence ----
export const EvidenceAPI = {
  upload: (assessmentId: string, controlId: string, file: File, onProgress?: (pct: number) => void) => {
    const form = new FormData();
    form.append("file", file);
    return api
      .post<Evidence>(`/evidence/${assessmentId}/${controlId}`, form, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (e) => {
          if (onProgress && e.total) onProgress(Math.round((e.loaded / e.total) * 100));
        },
      })
      .then((r) => r.data);
  },
  list: (assessmentId: string) => api.get<Evidence[]>(`/evidence/${assessmentId}`).then((r) => r.data),
  delete: (evidenceId: string) => api.delete(`/evidence/${evidenceId}`).then((r) => r.data),
  verify: (evidenceId: string) => api.post<Evidence>(`/evidence/${evidenceId}/verify`).then((r) => r.data),
  reject: (evidenceId: string) => api.post<Evidence>(`/evidence/${evidenceId}/reject`).then((r) => r.data),
};

// ---- Probe ----
// Script downloads must go through the authenticated axios instance (not a
// plain <a href>) because the endpoint requires a Bearer token — the
// downloaded script embeds a sensitive Ed25519 private key, so it can't be
// served anonymously. We fetch the text, then hand the browser a blob to
// save under a real filename.
async function downloadProbeScript(kind: "powershell" | "bash") {
  const path = kind === "powershell" ? "/probe/download/powershell" : "/probe/download/bash";
  const filename = kind === "powershell" ? "verify_probe.ps1" : "verify_probe.sh";
  const response = await api.get<string>(path, { responseType: "text" });
  const blob = new Blob([response.data], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export const ProbeAPI = {
  runs: (assessmentId: string) => api.get<ProbeRun[]>(`/probe/runs/${assessmentId}`).then((r) => r.data),
  downloadPowershell: () => downloadProbeScript("powershell"),
  downloadBash: () => downloadProbeScript("bash"),
};

// ---- Backup ----
export const BackupAPI = {
  get: (assessmentId: string) => api.get<BackupResilience | null>(`/backup/${assessmentId}`).then((r) => r.data),
  upsert: (assessmentId: string, payload: Partial<BackupResilience>) =>
    api.put<BackupResilience>(`/backup/${assessmentId}`, payload).then((r) => r.data),
};

// ---- Detection / Logs / Dwell-time ----
export const DetectionAPI = {
  matrix: (assessmentId: string) => api.get<DetectionStage[]>(`/detection/${assessmentId}/matrix`).then((r) => r.data),
  dwellTime: (assessmentId: string) => api.get<DwellTimeReadiness>(`/detection/${assessmentId}/dwell-time`).then((r) => r.data),
};

// ---- Regulatory Compliance ----
export const RegulatoryAPI = {
  compliance: (assessmentId: string) => api.get<RegulatoryCompliance>(`/regulatory/${assessmentId}/compliance`).then((r) => r.data),
};

export const LogsAPI = {
  upsertSources: (assessmentId: string, sources: LogSource[]) =>
    api.put<LogSource[]>(`/logs/${assessmentId}/sources`, sources).then((r) => r.data),
  gapAnalysis: (assessmentId: string) => api.get<LogGapAnalysis>(`/logs/${assessmentId}/gap-analysis`).then((r) => r.data),
};

// ---- Canary ----
export const CanaryAPI = {
  deploy: (canary_count = 5, assessmentId?: string) =>
    api.post<Canary[]>("/canary/deploy", { canary_count }, { params: assessmentId ? { assessment_id: assessmentId } : {} }).then((r) => r.data),
  list: () => api.get<Canary[]>("/canary").then((r) => r.data),
  events: () => api.get<CanaryEvent[]>("/canary/events").then((r) => r.data),
  simulate: (canaryId: string) => api.post<CanaryEvent>(`/canary/simulate/${canaryId}`).then((r) => r.data),
  streamUrl: (token: string) => `${api.defaults.baseURL}/canary/stream?token=${encodeURIComponent(token)}`,
};

// ---- Remediation ----
export const RemediationAPI = {
  generate: (assessmentId: string) => api.post<RemediationItem[]>(`/remediation/${assessmentId}/generate`).then((r) => r.data),
  list: (assessmentId: string, filters?: Record<string, string | undefined>) =>
    api.get<RemediationItem[]>(`/remediation/${assessmentId}`, { params: filters }).then((r) => r.data),
};

// ---- Dashboard ----
export const DashboardAPI = {
  get: (assessmentId: string) => api.get<DashboardData>(`/dashboard/${assessmentId}`).then((r) => r.data),
};

// ---- Reports ----
export const ReportsAPI = {
  generate: (assessmentId: string, report_type: "executive" | "technical") =>
    api.post<Report>(`/reports/${assessmentId}/generate`, { report_type }).then((r) => r.data),
  list: (assessmentId: string) => api.get<Report[]>(`/reports/${assessmentId}`).then((r) => r.data),
};

// ---- Benchmarking / Trends ----
export const BenchmarkingAPI = {
  get: (orgId: string) => api.get<Benchmark>(`/benchmarking/${orgId}`).then((r) => r.data),
  trends: (orgId: string) => api.get<Trend>(`/trends/${orgId}`).then((r) => r.data),
};

// ---- Ledger ----
export const LedgerAPI = {
  entries: () => api.get<LedgerEntry[]>("/ledger/entries").then((r) => r.data),
  verify: () => api.post<LedgerVerifyResult>("/ledger/verify").then((r) => r.data),
  demoTamper: (sequence: number) => api.post<LedgerEntry>(`/ledger/demo-tamper/${sequence}`).then((r) => r.data),
  fabricStatus: () => api.get<FabricStatus>("/ledger/fabric-status").then((r) => r.data),
};

// ---- Admin / Oversight ----
export const AdminAPI = {
  organisations: () => api.get<AdminOrganisation[]>("/admin/organisations").then((r) => r.data),
  auditLogs: (limit = 200) => api.get(`/admin/audit-logs`, { params: { limit } }).then((r) => r.data),
};

// ---- Assist (optional LLM) ----
export const AssistAPI = {
  available: () => api.get<{ available: boolean }>("/assist/available").then((r) => r.data),
  explain: (content: string) => api.post<{ available: boolean; explanation?: string }>("/assist/explain", { content }).then((r) => r.data),
};
