import { useDetectionMatrix, useLogGapAnalysis, useUpsertLogSources } from "@/api/hooks";
import { DetectionMatrix } from "@/components/DetectionMatrix";
import { EmptyState } from "@/components/EmptyState";
import { Layout } from "@/components/Layout";
import { useCurrentAssessmentId } from "@/lib/currentAssessment";
import { DEFAULT_LOG_SOURCES } from "@/lib/defaultLogSources";
import type { LogSource } from "@/types";

export default function DetectionMatrixPage() {
  const { assessmentId } = useCurrentAssessmentId();
  const { data: stages, isLoading } = useDetectionMatrix(assessmentId ?? undefined);
  const { data: logGaps } = useLogGapAnalysis(assessmentId ?? undefined);
  const upsertSources = useUpsertLogSources(assessmentId ?? "");

  if (!assessmentId) {
    return (
      <Layout title="Detection Matrix">
        <EmptyState title="No active assessment" description="Start an assessment from the Overview page first." />
      </Layout>
    );
  }

  const editableSources = logGaps?.sources.length ? logGaps.sources : DEFAULT_LOG_SOURCES;

  function handleToggleSource(source: LogSource) {
    const next = editableSources.map((s) =>
      s.source_name === source.source_name ? { ...s, enabled: !s.enabled } : s
    );
    upsertSources.mutate(next);
  }

  return (
    <Layout
      title="Detection Matrix"
      subtitle="Ransomware pre-encryption kill chain coverage, derived from your answers and log sources — not fabricated."
    >
      {isLoading ? (
        <p className="text-sm text-muted">Loading…</p>
      ) : (
        <DetectionMatrix
          stages={stages ?? []}
          sources={editableSources}
          onToggleSource={handleToggleSource}
          togglingSources={upsertSources.isPending}
        />
      )}
      <p className="text-[11px] text-muted pt-4">
        Technique IDs link to the official MITRE ATT&CK® knowledge base. MITRE ATT&CK is a registered trademark of
        The MITRE Corporation; technique data is sourced from the official STIX 2.1 dataset and used here for
        attribution/reference only. "Industry benchmark" figures are CIS Community Defense Model v2.0's published
        ransomware-attack-pattern coverage percentages per ATT&CK tactic — an external reference point, not a claim
        about this organisation's own posture.
      </p>
    </Layout>
  );
}
