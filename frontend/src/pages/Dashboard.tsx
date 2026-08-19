import { useDashboard } from "@/api/hooks";
import { AssuranceGauge } from "@/components/AssuranceGauge";
import { DetectionMatrix } from "@/components/DetectionMatrix";
import { EmptyState } from "@/components/EmptyState";
import { Layout } from "@/components/Layout";
import { MaturityRadar } from "@/components/MaturityRadar";
import { ScoreCard } from "@/components/ScoreCard";
import { useCurrentAssessmentId } from "@/lib/currentAssessment";

export default function Dashboard() {
  const { assessmentId } = useCurrentAssessmentId();
  const { data, isLoading } = useDashboard(assessmentId ?? undefined);

  if (!assessmentId) {
    return (
      <Layout title="Dashboard">
        <EmptyState title="No active assessment" description="Start an assessment from the Overview page first." />
      </Layout>
    );
  }

  if (isLoading || !data) {
    return (
      <Layout title="Dashboard">
        <p className="text-sm text-muted">Loading…</p>
      </Layout>
    );
  }

  const { assessment, detection_matrix, evidence_count, probe_status } = data;

  return (
    <Layout title="Dashboard" subtitle="Every number here is computed server-side from stored assessment data.">
      <div className="space-y-6">
        <div className="card bg-bg-raised border-accent/20">
          <p className="text-xs text-light/80 leading-relaxed">
            <strong className="text-accent-ink">Maturity</strong> represents what the organisation reports through its
            assessment responses. <strong className="text-accent-ink">Assurance</strong> represents how much of that
            claim is supported by evidence or automated verification.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <ScoreCard label="Maturity Score" value={assessment.maturity_score?.toFixed(1) ?? "—"} suffix="/5" accent />
          <ScoreCard label="Assurance Score" value={assessment.assurance_score?.toFixed(0) ?? "—"} suffix="%" />
          <ScoreCard label="Completion" value={assessment.progress.toFixed(0)} suffix="%" />
          <ScoreCard label="Probe Status" value={probe_status.replace("_", " ")} hint={`${evidence_count} evidence file(s)`} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <div className="label-text mb-3">Domain Maturity</div>
            <MaturityRadar domainScores={assessment.domain_scores} />
          </div>
          <div className="card flex flex-col justify-center">
            <div className="label-text mb-3">Assurance</div>
            <AssuranceGauge assuranceScore={assessment.assurance_score ?? 0} />
          </div>
        </div>

        <div className="card">
          <div className="label-text mb-3">High-Impact Unverified Controls</div>
          {!assessment.high_impact_gaps.length ? (
            <p className="text-sm text-light/70">No high-impact controls are currently flagged as unverified.</p>
          ) : (
            <div className="space-y-2">
              {assessment.high_impact_gaps.map((g) => (
                <div key={g.control_id} className="flex items-center justify-between bg-bg-raised rounded px-3 py-2 text-xs">
                  <div>
                    <span className="text-light">{g.title}</span>
                    <span className="text-muted ml-2">{g.domain}</span>
                  </div>
                  <span className="text-red-400">{g.reason}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div>
          <div className="label-text mb-3">Detection Coverage</div>
          <DetectionMatrix stages={detection_matrix} />
        </div>
      </div>
    </Layout>
  );
}
