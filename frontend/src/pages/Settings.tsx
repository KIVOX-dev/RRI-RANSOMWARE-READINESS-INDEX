import { useOrganisation } from "@/api/hooks";
import { Layout } from "@/components/Layout";

export default function Settings() {
  const { data: org } = useOrganisation();

  return (
    <Layout title="Settings">
      <div className="space-y-6 max-w-2xl">
        <div className="card">
          <div className="label-text mb-3">Organisation</div>
          <div className="text-sm text-light">{org?.name}</div>
          <div className="text-xs text-muted mt-1">{org?.sector} {org?.size ? `· ${org.size}` : ""}</div>
          {org?.is_synthetic && (
            <span className="inline-block mt-2 text-[10px] bg-accent text-ink px-2 py-1 rounded font-semibold">
              SAMPLE / SYNTHETIC DATA
            </span>
          )}
        </div>

        <div className="card">
          <div className="label-text mb-3">Data Retention Policy</div>
          <p className="text-xs text-light/70 leading-relaxed">
            Evidence files are retained for the lifetime of the assessment they support and can be deleted at any
            time from the Evidence page, which immediately removes the underlying object storage file and
            recalculates the Assurance Score. Generated reports are retained as immutable, versioned artifacts and
            referenced by the Integrity Ledger; deleting a report does not remove its ledger entry, which exists to
            preserve historical integrity verification.
          </p>
        </div>
      </div>
    </Layout>
  );
}
