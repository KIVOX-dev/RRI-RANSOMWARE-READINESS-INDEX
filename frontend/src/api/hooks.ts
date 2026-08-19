import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  AdminAPI, AssessmentsAPI, AssistAPI, BackupAPI, BenchmarkingAPI, CanaryAPI, DashboardAPI,
  DetectionAPI, EvidenceAPI, LedgerAPI, LogsAPI, OrgAPI, ProbeAPI, QuestionsAPI, RegulatoryAPI, RemediationAPI,
  ReportsAPI,
} from "@/api/client";
import type { LogSource } from "@/types";

export function useOrganisation() {
  return useQuery({ queryKey: ["organisation", "me"], queryFn: OrgAPI.me });
}

export function useOrganisationDirectory(enabled: boolean) {
  return useQuery({ queryKey: ["organisation", "directory"], queryFn: OrgAPI.directory, enabled });
}

export function useQuestions(sector?: string, role?: string, language = "en", mode: "basic" | "full" = "full") {
  return useQuery({
    queryKey: ["questions", sector, role, language, mode],
    queryFn: () => QuestionsAPI.list(sector!, role!, language, mode),
    enabled: Boolean(sector && role),
  });
}

export function useAssessments() {
  return useQuery({ queryKey: ["assessments"], queryFn: AssessmentsAPI.list });
}

export function useAssessment(id?: string) {
  return useQuery({
    queryKey: ["assessment", id],
    queryFn: () => AssessmentsAPI.get(id!),
    enabled: Boolean(id),
    refetchInterval: false,
  });
}

export function useStartAssessment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: AssessmentsAPI.start,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["assessments"] }),
  });
}

export function useSubmitAnswer(assessmentId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ controlId, answer }: { controlId: string; answer: unknown }) =>
      AssessmentsAPI.submitAnswer(assessmentId, controlId, answer),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["assessment", assessmentId] });
      qc.invalidateQueries({ queryKey: ["answers", assessmentId] });
    },
  });
}

export function useAnswers(assessmentId?: string) {
  return useQuery({
    queryKey: ["answers", assessmentId],
    queryFn: () => AssessmentsAPI.listAnswers(assessmentId!),
    enabled: Boolean(assessmentId),
  });
}

export function useCompleteAssessment(assessmentId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => AssessmentsAPI.complete(assessmentId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["assessment", assessmentId] });
      qc.invalidateQueries({ queryKey: ["assessments"] });
    },
  });
}

export function useEvidence(assessmentId?: string) {
  return useQuery({
    queryKey: ["evidence", assessmentId],
    queryFn: () => EvidenceAPI.list(assessmentId!),
    enabled: Boolean(assessmentId),
  });
}

export function useUploadEvidence(assessmentId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ controlId, file, onProgress }: { controlId: string; file: File; onProgress?: (p: number) => void }) =>
      EvidenceAPI.upload(assessmentId, controlId, file, onProgress),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["evidence", assessmentId] });
      qc.invalidateQueries({ queryKey: ["assessment", assessmentId] });
    },
  });
}

export function useDeleteEvidence(assessmentId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (evidenceId: string) => EvidenceAPI.delete(evidenceId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["evidence", assessmentId] });
      qc.invalidateQueries({ queryKey: ["assessment", assessmentId] });
    },
  });
}

export function useVerifyEvidence(assessmentId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (evidenceId: string) => EvidenceAPI.verify(evidenceId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["evidence", assessmentId] });
      qc.invalidateQueries({ queryKey: ["assessment", assessmentId] });
    },
  });
}

export function useRejectEvidence(assessmentId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (evidenceId: string) => EvidenceAPI.reject(evidenceId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["evidence", assessmentId] });
      qc.invalidateQueries({ queryKey: ["assessment", assessmentId] });
    },
  });
}

export function useProbeRuns(assessmentId?: string) {
  return useQuery({
    queryKey: ["probe-runs", assessmentId],
    queryFn: () => ProbeAPI.runs(assessmentId!),
    enabled: Boolean(assessmentId),
    refetchInterval: 5000,
  });
}

export function useBackup(assessmentId?: string) {
  return useQuery({
    queryKey: ["backup", assessmentId],
    queryFn: () => BackupAPI.get(assessmentId!),
    enabled: Boolean(assessmentId),
  });
}

export function useUpsertBackup(assessmentId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Parameters<typeof BackupAPI.upsert>[1]) => BackupAPI.upsert(assessmentId, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["backup", assessmentId] }),
  });
}

export function useDetectionMatrix(assessmentId?: string) {
  return useQuery({
    queryKey: ["detection-matrix", assessmentId],
    queryFn: () => DetectionAPI.matrix(assessmentId!),
    enabled: Boolean(assessmentId),
    refetchInterval: 5000,
  });
}

export function useDwellTime(assessmentId?: string) {
  return useQuery({
    queryKey: ["dwell-time", assessmentId],
    queryFn: () => DetectionAPI.dwellTime(assessmentId!),
    enabled: Boolean(assessmentId),
  });
}

export function useRegulatoryCompliance(assessmentId?: string) {
  return useQuery({
    queryKey: ["regulatory-compliance", assessmentId],
    queryFn: () => RegulatoryAPI.compliance(assessmentId!),
    enabled: Boolean(assessmentId),
  });
}

export function useLogGapAnalysis(assessmentId?: string) {
  return useQuery({
    queryKey: ["log-gap-analysis", assessmentId],
    queryFn: () => LogsAPI.gapAnalysis(assessmentId!),
    enabled: Boolean(assessmentId),
    refetchInterval: 5000,
  });
}

export function useUpsertLogSources(assessmentId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (sources: LogSource[]) => LogsAPI.upsertSources(assessmentId, sources),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["log-gap-analysis", assessmentId] });
      qc.invalidateQueries({ queryKey: ["detection-matrix", assessmentId] });
    },
  });
}

export function useCanaries() {
  return useQuery({ queryKey: ["canaries"], queryFn: CanaryAPI.list });
}

export function useCanaryEvents() {
  return useQuery({ queryKey: ["canary-events"], queryFn: CanaryAPI.events, refetchInterval: 10000 });
}

export function useDeployCanaries() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ count, assessmentId }: { count: number; assessmentId?: string }) => CanaryAPI.deploy(count, assessmentId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["canaries"] }),
  });
}

export function useSimulateCanary() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (canaryId: string) => CanaryAPI.simulate(canaryId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["canary-events"] });
      qc.invalidateQueries({ queryKey: ["canaries"] });
    },
  });
}

export function useRemediation(assessmentId?: string, filters?: Record<string, string | undefined>) {
  return useQuery({
    queryKey: ["remediation", assessmentId, filters],
    queryFn: () => RemediationAPI.list(assessmentId!, filters),
    enabled: Boolean(assessmentId),
  });
}

export function useGenerateRemediation(assessmentId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => RemediationAPI.generate(assessmentId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["remediation", assessmentId] }),
  });
}

export function useDashboard(assessmentId?: string) {
  return useQuery({
    queryKey: ["dashboard", assessmentId],
    queryFn: () => DashboardAPI.get(assessmentId!),
    enabled: Boolean(assessmentId),
  });
}

export function useReports(assessmentId?: string) {
  return useQuery({
    queryKey: ["reports", assessmentId],
    queryFn: () => ReportsAPI.list(assessmentId!),
    enabled: Boolean(assessmentId),
  });
}

export function useGenerateReport(assessmentId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (reportType: "executive" | "technical") => ReportsAPI.generate(assessmentId, reportType),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["reports", assessmentId] }),
  });
}

export function useBenchmark(orgId?: string) {
  return useQuery({
    queryKey: ["benchmark", orgId],
    queryFn: () => BenchmarkingAPI.get(orgId!),
    enabled: Boolean(orgId),
  });
}

export function useTrends(orgId?: string) {
  return useQuery({
    queryKey: ["trends", orgId],
    queryFn: () => BenchmarkingAPI.trends(orgId!),
    enabled: Boolean(orgId),
  });
}

export function useLedgerEntries() {
  return useQuery({ queryKey: ["ledger-entries"], queryFn: LedgerAPI.entries });
}

export function useFabricStatus() {
  return useQuery({ queryKey: ["fabric-status"], queryFn: LedgerAPI.fabricStatus, refetchInterval: 10000 });
}

export function useVerifyLedger() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: LedgerAPI.verify,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["ledger-entries"] }),
  });
}

export function useDemoTamper() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (sequence: number) => LedgerAPI.demoTamper(sequence),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["ledger-entries"] }),
  });
}

export function useAdminOrganisations() {
  return useQuery({ queryKey: ["admin-organisations"], queryFn: AdminAPI.organisations });
}

export function useAuditLogs() {
  return useQuery({ queryKey: ["audit-logs"], queryFn: () => AdminAPI.auditLogs() });
}

export function useAssistAvailable() {
  return useQuery({ queryKey: ["assist-available"], queryFn: AssistAPI.available, staleTime: 60000 });
}
