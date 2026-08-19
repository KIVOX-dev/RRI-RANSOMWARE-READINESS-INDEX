import clsx from "clsx";
import type { ProbeRun } from "@/types";
import { EmptyState } from "@/components/EmptyState";

const RESULT_COLOR: Record<string, string> = {
  pass: "text-accent-ink",
  fail: "text-red-400",
  unknown: "text-muted",
  not_applicable: "text-muted",
};

export function ProbeStatus({ runs }: { runs: ProbeRun[] }) {
  if (!runs.length) {
    return <EmptyState title="No probe results yet" description="Run the verification probe script and it will appear here once ingested." />;
  }

  const latest = runs[0];

  return (
    <div className="space-y-4">
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <div className="label-text">Latest run</div>
            <div className="text-light text-sm mt-1">{new Date(latest.timestamp).toLocaleString()}</div>
            <div className="text-xs text-muted mt-1">Host fingerprint: {latest.host_fingerprint.slice(0, 16)}…</div>
          </div>
          <span
            className={clsx(
              "px-3 py-1 rounded text-xs font-medium uppercase",
              latest.verification_status === "verified" ? "bg-accent text-ink" : "bg-red-500/20 text-red-400 border border-red-500/40"
            )}
          >
            {latest.verification_status}
          </span>
        </div>
        <p className="text-xs text-muted mt-3 border-t border-border pt-3">{latest.note}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {latest.checks.map((check) => (
          <div key={check.check_id} className="card flex items-center justify-between py-3">
            <div>
              <div className="text-sm text-light">{check.label || check.check_id}</div>
              <div className="text-[10px] text-muted uppercase tracking-wide">{check.check_id}</div>
            </div>
            <span className={clsx("text-xs font-semibold uppercase", RESULT_COLOR[check.result] || "text-muted")}>{check.result}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
