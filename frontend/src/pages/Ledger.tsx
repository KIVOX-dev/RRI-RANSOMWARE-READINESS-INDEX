import { useState } from "react";
import { useDemoTamper, useFabricStatus, useLedgerEntries, useVerifyLedger } from "@/api/hooks";
import { EmptyState } from "@/components/EmptyState";
import { Layout } from "@/components/Layout";
import { LedgerVerification } from "@/components/LedgerVerification";
import { useAuth } from "@/lib/auth";
import type { LedgerVerifyResult } from "@/types";

export default function Ledger() {
  const { user } = useAuth();
  const { data: entries, isLoading } = useLedgerEntries();
  const { data: fabric } = useFabricStatus();
  const verify = useVerifyLedger();
  const demoTamper = useDemoTamper();
  const [result, setResult] = useState<LedgerVerifyResult | null>(null);

  return (
    <Layout
      title="Integrity Ledger"
      subtitle="An append-only, Ed25519-signed SHA-256 hash chain — a local signed hash chain, not a blockchain."
    >
      <div className="space-y-6">
        <LedgerVerification
          result={result}
          verifying={verify.isPending}
          onVerify={() => verify.mutateAsync().then(setResult)}
        />

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <div className="label-text mb-1">Hyperledger Fabric On-Chain Anchor (optional stretch layer)</div>
              <p className="text-xs text-muted max-w-2xl">
                Every ledger record above is also best-effort anchored on a local, single-org Hyperledger Fabric
                network via a minimal chaincode transaction. This is <strong className="text-light">not</strong> the
                source of truth — the signed hash chain is — and the app keeps working normally if this layer is
                unreachable.
              </p>
            </div>
            <span
              className={`shrink-0 ml-4 px-3 py-1 rounded text-xs font-medium uppercase ${
                fabric?.connected ? "bg-accent text-ink" : "bg-red-500/15 text-red-400 border border-red-500/40"
              }`}
            >
              {fabric === undefined ? "checking…" : fabric.connected ? "connected" : "unreachable"}
            </span>
          </div>
          {fabric?.connected && (
            <div className="mt-3 text-xs text-muted font-mono">
              Chaincode <span className="text-light">{fabric.contract_address}</span> · {fabric.anchor_count} anchor(s) recorded on-chain
            </div>
          )}
        </div>

        {user?.role === "platform_admin" && entries && entries.some((e) => e.organisation_id === user.organisation_id) && (
          <div className="card border-red-500/30">
            <div className="label-text mb-2">Demo Tamper (Admin only)</div>
            <p className="text-xs text-muted mb-3">
              Intentionally corrupts a stored record's payload hash so the next Verify demonstrates
              "Integrity Violation Detected". For demonstration purposes only — only your own organisation's records
              can be tampered here, not a linked parent/sub-organisation's.
            </p>
            <div className="flex items-center gap-2">
              <select id="tamper-seq" className="input-field w-auto text-xs py-1.5">
                {entries.filter((e) => e.organisation_id === user.organisation_id).map((e) => (
                  <option key={e.id} value={e.sequence}>Record #{e.sequence}</option>
                ))}
              </select>
              <button
                className="btn-secondary text-xs border-red-500/40 text-red-400 hover:border-red-500"
                onClick={() => {
                  const select = document.getElementById("tamper-seq") as HTMLSelectElement;
                  demoTamper.mutate(Number(select.value));
                }}
                disabled={demoTamper.isPending}
              >
                Tamper selected record
              </button>
            </div>
          </div>
        )}

        <div>
          <div className="label-text mb-3">Ledger Records</div>
          {isLoading && <p className="text-sm text-muted">Loading…</p>}
          {!isLoading && !entries?.length && <EmptyState title="No ledger entries yet" description="Complete an assessment or generate a report to create the first ledger entry." />}
          <div className="space-y-2">
            {entries?.map((e) => (
              <div
                key={e.id}
                className={`card text-xs font-mono ${e.record_type === "sub_organisation_request" ? "border-accent/50" : ""}`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-light">
                    Record #{e.sequence} — <span className="text-muted">{e.organisation_name}</span>
                  </span>
                  <span className={e.verification_status === "verified" ? "text-accent-ink" : e.verification_status === "invalid" ? "text-red-400" : "text-muted"}>
                    {e.verification_status}
                  </span>
                </div>
                {e.record_type === "sub_organisation_request" && (
                  <div className="mb-2 px-2 py-1.5 rounded bg-accent/10 border border-accent/30 text-accent-ink not-italic">
                    Sub-organisation request — verified automatically the next time you click Verify above.
                  </div>
                )}
                <div className="text-muted space-y-1 break-all">
                  <div>Assessment: {e.assessment_id ?? "—"} {e.report_id ? `· Report: ${e.report_id}` : ""}</div>
                  <div>Timestamp: {new Date(e.timestamp).toLocaleString()}</div>
                  <div>Payload hash: {e.payload_hash}</div>
                  <div>Previous hash: {e.previous_record_hash}</div>
                  <div>Record hash: {e.record_hash}</div>
                  <div>Signature: {e.signature.slice(0, 40)}…</div>
                  <div>
                    Fabric anchor:{" "}
                    {e.fabric_anchor ? (
                      <span className="text-accent-ink">{e.fabric_anchor}</span>
                    ) : (
                      <span className="text-muted italic">not anchored (Fabric was unreachable when this record was created)</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  );
}
