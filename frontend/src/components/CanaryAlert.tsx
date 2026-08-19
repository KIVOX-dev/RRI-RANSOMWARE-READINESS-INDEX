import clsx from "clsx";
import type { CanaryEvent } from "@/types";

const SEVERITY_STYLES: Record<string, string> = {
  critical: "border-red-500/50 bg-red-500/10 text-red-400",
  high: "border-accent/50 bg-accent/10 text-accent-ink",
  medium: "border-border bg-bg-raised text-light",
  low: "border-border bg-bg-raised text-muted",
};

export function CanaryAlert({ event }: { event: CanaryEvent }) {
  return (
    <div className={clsx("rounded-md border px-4 py-3 flex items-center justify-between", SEVERITY_STYLES[event.severity] || SEVERITY_STYLES.medium)}>
      <div>
        <div className="text-sm font-medium">{event.event_type.replace(/_/g, " ")}</div>
        <div className="text-xs opacity-80 mt-0.5">{event.file_path.split(/[/\\]/).pop()}</div>
        <div className="text-[10px] opacity-60 mt-0.5">{new Date(event.timestamp).toLocaleString()}</div>
      </div>
      <span className="text-[10px] uppercase tracking-wide font-semibold">{event.severity}</span>
    </div>
  );
}
