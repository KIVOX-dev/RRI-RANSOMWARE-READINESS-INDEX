import type { Report } from "@/types";

export function ReportCard({ report }: { report: Report }) {
  return (
    <div className="card flex items-center justify-between">
      <div>
        <div className="text-light text-sm font-medium capitalize">{report.report_type} report · v{report.version}</div>
        <div className="text-xs text-muted mt-1">Generated {new Date(report.generated_at).toLocaleString()}</div>
        <div className="text-[10px] text-muted mt-1 font-mono">SHA-256 {report.checksum.slice(0, 24)}…</div>
      </div>
      {report.download_url && (
        <a href={report.download_url} target="_blank" rel="noreferrer" className="btn-secondary text-xs">
          Download PDF
        </a>
      )}
    </div>
  );
}
