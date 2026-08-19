import clsx from "clsx";
import type { DetectionStage, LogSource } from "@/types";
import { EmptyState } from "@/components/EmptyState";

const STATUS_STYLES: Record<string, string> = {
  covered: "bg-accent text-ink",
  partial: "bg-accent/25 text-accent-ink border border-accent/40",
  blind: "bg-bg-raised text-muted border border-border",
};

export function DetectionMatrix({
  stages,
  sources = [],
  onToggleSource,
  togglingSources = false,
}: {
  stages: DetectionStage[];
  sources?: LogSource[];
  onToggleSource?: (source: LogSource) => void;
  togglingSources?: boolean;
}) {
  if (!stages.length) {
    return <EmptyState title="No detection data yet" description="Detection coverage is derived from answered controls and log sources." />;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
      {stages.map((stage) => {
        const relevantSources = sources.filter((s) => s.covered_stages.includes(stage.stage));
        return (
        <div key={stage.stage} className="card flex flex-col gap-2">
          <div className="text-xs text-muted uppercase tracking-wide">{stage.stage}</div>
          <span className={clsx("self-start px-2 py-1 rounded text-xs font-medium uppercase", STATUS_STYLES[stage.status])}>
            {stage.status}
          </span>
          <div className="text-xs text-muted">Log coverage: {stage.log_coverage}%</div>
          {relevantSources.length > 0 && onToggleSource && (
            <div className="flex flex-col gap-1 pt-1 border-t border-border/60">
              <div className="text-[10px] text-muted uppercase tracking-wide">Log sources</div>
              <div className="flex flex-wrap gap-1">
                {relevantSources.map((s) => (
                  <button
                    key={s.source_name}
                    type="button"
                    disabled={togglingSources}
                    onClick={() => onToggleSource(s)}
                    title={s.enabled ? "Enabled — click to disable" : "Disabled — click to enable"}
                    className={clsx(
                      "px-1.5 py-0.5 rounded text-[10px] border transition-colors disabled:opacity-50",
                      s.enabled
                        ? "bg-accent text-ink border-accent"
                        : "bg-bg-raised text-muted border-border hover:text-ink hover:border-accent"
                    )}
                  >
                    {s.source_name}
                  </button>
                ))}
              </div>
            </div>
          )}
          {stage.cis_cdm_benchmark && (
            <div className="text-[10px] text-muted" title={`${stage.cis_cdm_benchmark.source.title} — ${stage.cis_cdm_benchmark.tactic} tactic, ransomware attack pattern`}>
              Industry benchmark (CIS CDM v2, ransomware): {stage.cis_cdm_benchmark.coverage_pct}% of ATT&CK techniques defendable
            </div>
          )}
          <p className="text-xs text-light/70 leading-relaxed">{stage.explanation}</p>
          {stage.attck_techniques.length > 0 && (
            <div className="flex flex-col gap-1 pt-1 border-t border-border/60">
              <div className="text-[10px] text-muted uppercase tracking-wide">Adversary techniques (MITRE ATT&CK)</div>
              <div className="flex flex-wrap gap-1">
                {stage.attck_techniques.map((t) => (
                  <a
                    key={t.technique_id}
                    href={t.url}
                    target="_blank"
                    rel="noreferrer"
                    title={t.name}
                    className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-bg-raised border border-border text-muted hover:text-ink hover:border-accent transition-colors"
                  >
                    {t.technique_id}
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>
        );
      })}
    </div>
  );
}
