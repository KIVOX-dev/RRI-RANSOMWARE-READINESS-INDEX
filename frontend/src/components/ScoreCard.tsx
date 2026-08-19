import clsx from "clsx";

export function ScoreCard({
  label,
  value,
  suffix = "",
  accent = false,
  hint,
}: {
  label: string;
  value: string | number;
  suffix?: string;
  accent?: boolean;
  hint?: string;
}) {
  return (
    <div className="card flex flex-col gap-1">
      <div className="label-text">{label}</div>
      <div className={clsx("text-3xl font-bold", accent ? "text-accent-ink" : "text-light")}>
        {value}
        <span className="text-lg font-normal text-muted ml-1">{suffix}</span>
      </div>
      {hint && <div className="text-xs text-muted mt-1">{hint}</div>}
    </div>
  );
}
