import { useState } from "react";
import { useGenerateReport, useReports } from "@/api/hooks";
import { EmptyState } from "@/components/EmptyState";
import { Layout } from "@/components/Layout";
import { ReportCard } from "@/components/ReportCard";
import { apiErrorMessage } from "@/lib/api";
import { useCurrentAssessmentId } from "@/lib/currentAssessment";

export default function Reports() {
  const { assessmentId } = useCurrentAssessmentId();
  const { data: reports, isLoading } = useReports(assessmentId ?? undefined);
  const generate = useGenerateReport(assessmentId ?? "");
  const [error, setError] = useState<string | null>(null);

  if (!assessmentId) {
    return (
      <Layout title="Reports">
        <EmptyState title="No active assessment" description="Start an assessment from the Overview page first." />
      </Layout>
    );
  }

  async function handleGenerate(type: "executive" | "technical") {
    setError(null);
    try {
      await generate.mutateAsync(type);
    } catch (e) {
      setError(apiErrorMessage(e));
    }
  }

  return (
    <Layout title="Reports" subtitle="Generated from live assessment data via Jinja2 → WeasyPrint, stored in object storage, and ledgered.">
      <div className="space-y-6">
        <div className="flex gap-3">
          <button className="btn-primary text-xs" onClick={() => handleGenerate("executive")} disabled={generate.isPending}>
            Generate Executive Report
          </button>
          <button className="btn-secondary text-xs" onClick={() => handleGenerate("technical")} disabled={generate.isPending}>
            Generate Technical Annexure
          </button>
        </div>
        {error && <p className="text-xs text-red-400">{error}</p>}
        {generate.isPending && <p className="text-xs text-muted">Generating report…</p>}

        <div className="space-y-3">
          {isLoading && <p className="text-sm text-muted">Loading…</p>}
          {!isLoading && !reports?.length && (
            <EmptyState title="No reports yet" description="Complete the assessment, then generate an executive or technical report." />
          )}
          {reports?.map((r) => <ReportCard key={r.id} report={r} />)}
        </div>
      </div>
    </Layout>
  );
}
