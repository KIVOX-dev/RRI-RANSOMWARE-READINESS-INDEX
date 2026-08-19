import { useDwellTime } from "@/api/hooks";
import { EmptyState } from "@/components/EmptyState";
import { Layout } from "@/components/Layout";
import { useCurrentAssessmentId } from "@/lib/currentAssessment";

function Bar({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="flex justify-between text-xs text-muted mb-1">
        <span>{label}</span>
        <span>{value.toFixed(0)}%</span>
      </div>
      <div className="h-2 bg-bg-raised rounded-full overflow-hidden">
        <div className="h-full bg-accent" style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}

export default function DwellTime() {
  const { assessmentId } = useCurrentAssessmentId();
  const { data, isLoading } = useDwellTime(assessmentId ?? undefined);

  if (!assessmentId) {
    return (
      <Layout title="Dwell-Time Readiness">
        <EmptyState title="No active assessment" description="Start an assessment from the Overview page first." />
      </Layout>
    );
  }

  return (
    <Layout title="Dwell-Time Readiness" subtitle="A readiness indicator derived from assessment signals — not a predictive model.">
      {isLoading || !data ? (
        <p className="text-sm text-muted">Loading…</p>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card flex flex-col items-center justify-center">
            <div className="text-5xl font-bold text-accent-ink">{data.score.toFixed(0)}</div>
            <div className="label-text mt-2">Overall Readiness</div>
          </div>
          <div className="card space-y-4">
            <Bar label="Credential Hygiene" value={data.credential_hygiene} />
            <Bar label="Password Reuse Signal" value={data.password_reuse_signal} />
            <Bar label="Privilege Practices" value={data.privilege_practices} />
            <Bar label="Lateral Movement Exposure" value={data.lateral_movement_exposure} />
          </div>
          <div className="card lg:col-span-2">
            <p className="text-xs text-light/70 leading-relaxed">{data.explanation}</p>
          </div>
        </div>
      )}
    </Layout>
  );
}
