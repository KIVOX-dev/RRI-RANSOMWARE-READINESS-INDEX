import type { Benchmark } from "@/types";
import { EmptyState } from "@/components/EmptyState";

export function BenchmarkCard({ benchmark }: { benchmark: Benchmark }) {
  if (!benchmark.available) {
    return <EmptyState title="Benchmark not available yet" description={benchmark.message} />;
  }

  return (
    <div className="space-y-4">
      {benchmark.is_synthetic_cohort && (
        <div className="text-[10px] uppercase tracking-wide bg-accent text-ink inline-block px-2 py-1 rounded font-semibold">
          Sample / Synthetic Data included in cohort
        </div>
      )}
      <div className="grid grid-cols-2 gap-4">
        <div className="card">
          <div className="label-text">Maturity Percentile</div>
          <div className="text-2xl font-bold text-accent-ink mt-1">{benchmark.maturity_percentile}th</div>
          <div className="text-xs text-muted mt-1">vs. {benchmark.cohort_size} organisations in {benchmark.sector}</div>
        </div>
        <div className="card">
          <div className="label-text">Assurance vs. Cohort Average</div>
          <div className="text-2xl font-bold text-light mt-1">
            {benchmark.assurance_comparison! >= 0 ? "+" : ""}
            {benchmark.assurance_comparison}pp
          </div>
        </div>
      </div>
      <div className="card">
        <div className="label-text mb-3">Domain Comparison</div>
        <div className="space-y-2">
          {benchmark.domain_comparison.map((d) => (
            <div key={d.domain} className="flex items-center justify-between text-sm">
              <span className="text-light/80">{d.domain}</span>
              <span className="text-muted">
                You: <span className="text-accent-ink font-medium">{d.organisation_score}</span> · Cohort avg: {d.cohort_average}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
