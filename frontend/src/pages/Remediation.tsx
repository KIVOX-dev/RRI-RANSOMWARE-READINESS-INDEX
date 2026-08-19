import { useState } from "react";
import { useGenerateRemediation, useRemediation } from "@/api/hooks";
import { EmptyState } from "@/components/EmptyState";
import { Layout } from "@/components/Layout";
import { RemediationQuadrant } from "@/components/RemediationQuadrant";
import { useCurrentAssessmentId } from "@/lib/currentAssessment";

const PRIORITY_STYLES: Record<string, string> = {
  critical: "text-red-400",
  high: "text-accent-ink",
  medium: "text-light",
  low: "text-muted",
};

export default function Remediation() {
  const { assessmentId } = useCurrentAssessmentId();
  const [filters, setFilters] = useState<{ domain?: string; impact?: string; effort?: string; priority?: string }>({});
  const { data: items, isLoading } = useRemediation(assessmentId ?? undefined, filters);
  const generate = useGenerateRemediation(assessmentId ?? "");

  if (!assessmentId) {
    return (
      <Layout title="Remediation">
        <EmptyState title="No active assessment" description="Start an assessment from the Overview page first." />
      </Layout>
    );
  }

  const domains = Array.from(new Set(items?.map((i) => i.domain) ?? []));

  return (
    <Layout title="Remediation Roadmap" subtitle="Generated from actual assessment gaps — priority is calculated, not templated.">
      <div className="space-y-6">
        <div className="flex items-center gap-3 flex-wrap">
          <button className="btn-primary text-xs" onClick={() => generate.mutate()} disabled={generate.isPending}>
            {generate.isPending ? "Generating…" : "Regenerate roadmap"}
          </button>
          <select className="input-field w-auto text-xs py-1.5" value={filters.domain ?? ""} onChange={(e) => setFilters((f) => ({ ...f, domain: e.target.value || undefined }))}>
            <option value="">All domains</option>
            {domains.map((d) => <option key={d} value={d}>{d}</option>)}
          </select>
          <select className="input-field w-auto text-xs py-1.5" value={filters.impact ?? ""} onChange={(e) => setFilters((f) => ({ ...f, impact: e.target.value || undefined }))}>
            <option value="">All impact</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <select className="input-field w-auto text-xs py-1.5" value={filters.effort ?? ""} onChange={(e) => setFilters((f) => ({ ...f, effort: e.target.value || undefined }))}>
            <option value="">All effort</option>
            <option value="low">Low</option>
            <option value="high">High</option>
          </select>
          <select className="input-field w-auto text-xs py-1.5" value={filters.priority ?? ""} onChange={(e) => setFilters((f) => ({ ...f, priority: e.target.value || undefined }))}>
            <option value="">All priority</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>

        <div className="card">
          <div className="label-text mb-3">Impact vs Effort</div>
          <RemediationQuadrant items={items ?? []} />
        </div>

        <div className="space-y-2">
          {isLoading && <p className="text-sm text-muted">Loading…</p>}
          {!isLoading && !items?.length && <EmptyState title="No remediation items" description="Generate the roadmap once you've answered assessment questions." />}
          {items?.map((item) => (
            <div key={item.id} className="card">
              <div className="flex items-center justify-between">
                <span className={`text-xs font-semibold uppercase ${PRIORITY_STYLES[item.priority]}`}>{item.priority}</span>
                <span className="text-[10px] text-muted uppercase">{item.domain} · {item.impact} impact · {item.effort} effort</span>
              </div>
              <div className="text-sm text-light mt-2">{item.issue}</div>
              <div className="text-xs text-muted mt-1">{item.reason}</div>
              <div className="text-xs text-accent-ink mt-2">→ {item.recommended_action}</div>
            </div>
          ))}
        </div>
      </div>
    </Layout>
  );
}
