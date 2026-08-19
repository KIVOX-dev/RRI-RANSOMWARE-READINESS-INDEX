import clsx from "clsx";
import type { LedgerVerifyResult } from "@/types";

export function LedgerVerification({ result, verifying, onVerify }: { result: LedgerVerifyResult | null; verifying: boolean; onVerify: () => void }) {
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <div className="label-text">Chain Verification</div>
          <div className="text-sm text-muted mt-1">Recalculates every hash link and Ed25519 signature in the ledger.</div>
        </div>
        <button className="btn-primary" onClick={onVerify} disabled={verifying}>
          {verifying ? "Verifying…" : "Verify"}
        </button>
      </div>
      {result && (
        <div
          className={clsx(
            "mt-4 rounded-md px-4 py-3 text-sm font-medium",
            result.verified ? "bg-accent/15 text-accent-ink border border-accent/40" : "bg-red-500/15 text-red-400 border border-red-500/40"
          )}
        >
          {result.verified ? "Integrity Verified" : "Integrity Violation Detected"}
          <div className="text-xs font-normal mt-1 opacity-80">{result.message}</div>
          {result.broken_at_sequence != null && (
            <div className="text-xs font-normal mt-1 opacity-80">Broken at record #{result.broken_at_sequence}</div>
          )}
        </div>
      )}
    </div>
  );
}
