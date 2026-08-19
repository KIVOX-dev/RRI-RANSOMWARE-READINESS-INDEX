import { useAdminOrganisations, useAuditLogs } from "@/api/hooks";
import { EmptyState } from "@/components/EmptyState";
import { Layout } from "@/components/Layout";
import { useAuth } from "@/lib/auth";

export default function Oversight() {
  const { user } = useAuth();
  const { data: orgs, isLoading } = useAdminOrganisations();
  const { data: auditLogs } = useAuditLogs();

  if (user?.role !== "platform_admin") {
    return (
      <Layout title="Regulator Console">
        <EmptyState title="Platform admin access required" description="This console is restricted to platform administrators. Access here is always audit-logged." />
      </Layout>
    );
  }

  return (
    <Layout title="Regulator / Oversight Console" subtitle="Platform-admin visibility across organisations. Every access here is audit-logged.">
      <div className="space-y-6">
        <div className="card overflow-x-auto">
          <div className="label-text mb-3">Organisations</div>
          {isLoading && <p className="text-sm text-muted">Loading…</p>}
          <table className="w-full text-xs">
            <thead>
              <tr className="text-muted uppercase tracking-wide text-left">
                <th className="py-2">Organisation</th>
                <th>Sector</th>
                <th>Status</th>
                <th>Maturity</th>
                <th>Assurance</th>
                <th>Completed</th>
                <th>Synthetic</th>
              </tr>
            </thead>
            <tbody>
              {orgs?.map((o) => (
                <tr key={o.id} className="border-t border-border">
                  <td className="py-2 text-light">{o.name}</td>
                  <td className="text-muted">{o.sector}</td>
                  <td className="text-muted">{o.assessment_status.replace("_", " ")}</td>
                  <td className="text-accent-ink">{o.maturity_score?.toFixed(1) ?? "—"}</td>
                  <td className="text-light">{o.assurance_score?.toFixed(0) ?? "—"}%</td>
                  <td className="text-muted">{o.completion_date ? new Date(o.completion_date).toLocaleDateString() : "—"}</td>
                  <td>{o.is_synthetic && <span className="text-[10px] bg-accent text-ink px-1.5 py-0.5 rounded font-semibold">SAMPLE</span>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="card">
          <div className="label-text mb-3">Recent Privileged Access (Audit Log)</div>
          <div className="space-y-1.5 max-h-64 overflow-y-auto">
            {auditLogs?.map((log: any) => (
              <div key={log.id} className="text-xs text-muted flex justify-between border-b border-border/50 pb-1.5">
                <span>{log.action}</span>
                <span>{new Date(log.timestamp).toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  );
}
