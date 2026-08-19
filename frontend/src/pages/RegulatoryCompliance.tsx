import clsx from "clsx";
import { useRegulatoryCompliance } from "@/api/hooks";
import { EmptyState } from "@/components/EmptyState";
import { Layout } from "@/components/Layout";
import { useCurrentAssessmentId } from "@/lib/currentAssessment";

const BASIS_LABEL: Record<string, string> = {
  self_reported: "self-reported",
  evidence_verified: "evidence-verified",
  technical_probe: "verification probe",
  measured_threshold: "measured value",
};

export default function RegulatoryCompliance() {
  const { assessmentId } = useCurrentAssessmentId();
  const { data, isLoading } = useRegulatoryCompliance(assessmentId ?? undefined);

  if (!assessmentId) {
    return (
      <Layout title="Regulatory Compliance">
        <EmptyState title="No active assessment" description="Start an assessment from the Overview page first." />
      </Layout>
    );
  }

  return (
    <Layout
      title="Regulatory Compliance"
      subtitle="Computed, per-framework verdicts derived from this assessment's actual answers — not static citations."
    >
      {isLoading || !data ? (
        <p className="text-sm text-muted">Loading…</p>
      ) : (
        <div className="space-y-4">
          {data.frameworks.map((framework) => {
            const metCount = framework.requirements.filter((r) => r.met).length;
            return (
              <div key={framework.framework} className="card">
                <div className="flex items-center justify-between mb-1">
                  <div>
                    <div className="text-sm font-medium text-light">{framework.framework}</div>
                    {framework.url && (
                      <a href={framework.url} target="_blank" rel="noreferrer" className="text-[11px] text-accent-ink underline">
                        {framework.url}
                      </a>
                    )}
                  </div>
                  <span
                    className={clsx(
                      "shrink-0 ml-4 px-3 py-1 rounded text-xs font-medium uppercase",
                      framework.verdict === "compliant" ? "bg-accent text-ink" : "bg-red-500/15 text-red-400 border border-red-500/40"
                    )}
                  >
                    {framework.verdict === "compliant" ? "Compliant" : "Non-Compliant"}
                  </span>
                </div>
                <p className="text-xs text-muted mb-3">{metCount} of {framework.requirements.length} requirements met</p>
                <div className="space-y-2">
                  {framework.requirements.map((req) => (
                    <div key={req.key} className="flex items-start gap-2 text-xs">
                      <span className={req.met ? "text-accent-ink" : "text-red-400"}>{req.met ? "✓" : "✗"}</span>
                      <div>
                        <span className="text-light/90">{req.description}</span>{" "}
                        <span className="text-muted">
                          ({BASIS_LABEL[req.basis] ?? req.basis}
                          {req.control_ids.length > 0 && <> · {req.control_ids.join(", ")}</>})
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}

          <p className="text-[11px] text-muted pt-2">{data.disclaimer}</p>
        </div>
      )}
    </Layout>
  );
}
