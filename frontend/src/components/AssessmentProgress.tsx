export function AssessmentProgress({ progress, answered, total }: { progress: number; answered: number; total: number }) {
  return (
    <div className="max-w-2xl">
      <div className="flex justify-between text-xs text-muted mb-1.5">
        <span>{answered} / {total} controls answered</span>
        <span>{progress.toFixed(0)}%</span>
      </div>
      <div className="h-2 bg-bg-raised rounded-full overflow-hidden">
        <div className="h-full bg-accent transition-all duration-300" style={{ width: `${Math.min(100, progress)}%` }} />
      </div>
    </div>
  );
}
