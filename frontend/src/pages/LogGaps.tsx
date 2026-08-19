import { useState } from "react";
import { useLogGapAnalysis, useUpsertLogSources } from "@/api/hooks";
import { EmptyState } from "@/components/EmptyState";
import { Layout } from "@/components/Layout";
import { useCurrentAssessmentId } from "@/lib/currentAssessment";
import { DEFAULT_LOG_SOURCES } from "@/lib/defaultLogSources";
import type { LogSource } from "@/types";

export default function LogGaps() {
  const { assessmentId } = useCurrentAssessmentId();
  const { data: analysis, isLoading } = useLogGapAnalysis(assessmentId ?? undefined);
  const upsert = useUpsertLogSources(assessmentId ?? "");
  const [sources, setSources] = useState<LogSource[]>(DEFAULT_LOG_SOURCES);

  if (!assessmentId) {
    return (
      <Layout title="Log Gaps">
        <EmptyState title="No active assessment" description="Start an assessment from the Overview page first." />
      </Layout>
    );
  }

  const editable = analysis?.sources.length ? analysis.sources : sources;

  function updateSource(idx: number, patch: Partial<LogSource>) {
    const next = [...editable];
    next[idx] = { ...next[idx], ...patch };
    if (analysis?.sources.length) {
      upsert.mutate(next);
    } else {
      setSources(next);
    }
  }

  return (
    <Layout title="Log Gaps" subtitle="Configure your log sources; coverage and detection gaps are computed from this.">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="label-text mb-3">Log Sources</div>
          <div className="space-y-3">
            {editable.map((s, idx) => (
              <div key={s.source_name} className="border border-border rounded-md p-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-light">{s.source_name}</span>
                  <label className="flex items-center gap-2 text-xs text-muted">
                    <input type="checkbox" checked={s.enabled} onChange={(e) => updateSource(idx, { enabled: e.target.checked })} />
                    Enabled
                  </label>
                </div>
                <div className="flex items-center gap-3 mt-2">
                  <label className="text-xs text-muted flex items-center gap-2">
                    Retention (days)
                    <input
                      type="number"
                      className="input-field w-20 py-1"
                      value={s.retention_days}
                      onChange={(e) => updateSource(idx, { retention_days: Number(e.target.value) })}
                    />
                  </label>
                  <label className="flex items-center gap-2 text-xs text-muted">
                    <input type="checkbox" checked={s.monitored} onChange={(e) => updateSource(idx, { monitored: e.target.checked })} />
                    Actively monitored
                  </label>
                </div>
              </div>
            ))}
          </div>
          {!analysis?.sources.length && (
            <button className="btn-primary text-xs mt-4" onClick={() => upsert.mutate(sources)} disabled={upsert.isPending}>
              {upsert.isPending ? "Saving…" : "Save log sources"}
            </button>
          )}
        </div>

        <div className="space-y-4">
          {isLoading && <p className="text-sm text-muted">Loading…</p>}
          {analysis && (
            <>
              <div className="card">
                <div className="label-text mb-2">Detectable stages</div>
                <p className="text-sm text-light/80">{analysis.detectable_stages.join(", ") || "None yet"}</p>
              </div>
              <div className="card">
                <div className="label-text mb-2">Partially detectable stages</div>
                <p className="text-sm text-light/80">{analysis.partial_stages.join(", ") || "None"}</p>
              </div>
              <div className="card">
                <div className="label-text mb-2">Blind stages</div>
                <p className="text-sm text-red-400">{analysis.blind_stages.join(", ") || "None"}</p>
              </div>
              <div className="card">
                <div className="label-text mb-2">Missing log sources</div>
                <p className="text-sm text-light/80">{analysis.missing_sources.join(", ") || "None missing"}</p>
              </div>
            </>
          )}
        </div>
      </div>
    </Layout>
  );
}
