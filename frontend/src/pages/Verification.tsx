import { useMemo, useState } from "react";
import { ProbeAPI } from "@/api/client";
import { useProbeRuns } from "@/api/hooks";
import { EmptyState } from "@/components/EmptyState";
import { Layout } from "@/components/Layout";
import { apiErrorMessage, getToken } from "@/lib/api";
import { useCurrentAssessmentId } from "@/lib/currentAssessment";
import { ProbeStatus } from "@/components/ProbeStatus";

type Platform = "powershell" | "bash";

function detectDefaultPlatform(): Platform {
  const ua = navigator.userAgent;
  return /Windows/i.test(ua) ? "powershell" : "bash";
}

export default function Verification() {
  const { assessmentId } = useCurrentAssessmentId();
  const { data: runs, dataUpdatedAt } = useProbeRuns(assessmentId ?? undefined);
  const [platform, setPlatform] = useState<Platform>(detectDefaultPlatform);
  const [commandCopied, setCommandCopied] = useState(false);
  const [downloading, setDownloading] = useState<Platform | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);
  const token = getToken() ?? "";

  const command = useMemo(() => {
    if (!assessmentId) return "";
    const backendUrl = `${window.location.protocol}//${window.location.hostname}:8010`;
    if (platform === "powershell") {
      // Fetches the script fresh and runs it in one paste — no separate
      // download/cd step, and since the file is written locally (not saved
      // by the browser), Windows never flags it as "from the internet", so
      // there's nothing to Unblock-File either.
      return (
        `$s = Invoke-RestMethod -Uri "${backendUrl}/probe/download/powershell" -Headers @{Authorization="Bearer ${token}"}; ` +
        `$p = Join-Path $env:TEMP "verify_probe.ps1"; [IO.File]::WriteAllText($p, $s); ` +
        `& $p -AssessmentId "${assessmentId}" -ApiToken "${token}" -BackendUrl "${backendUrl}"`
      );
    }
    return (
      `curl -s "${backendUrl}/probe/download/bash" -H "Authorization: Bearer ${token}" -o /tmp/verify_probe.sh && ` +
      `chmod +x /tmp/verify_probe.sh && /tmp/verify_probe.sh --assessment-id "${assessmentId}" --token "${token}"`
    );
  }, [assessmentId, platform, token]);

  if (!assessmentId) {
    return (
      <Layout title="Verification">
        <EmptyState title="No active assessment" description="Start an assessment from the Overview page first." />
      </Layout>
    );
  }

  async function copyCommand() {
    await navigator.clipboard.writeText(command);
    setCommandCopied(true);
    setTimeout(() => setCommandCopied(false), 1800);
  }

  async function handleDownload(kind: Platform) {
    setDownloadError(null);
    setDownloading(kind);
    try {
      if (kind === "powershell") await ProbeAPI.downloadPowershell();
      else await ProbeAPI.downloadBash();
    } catch (e) {
      setDownloadError(apiErrorMessage(e));
    } finally {
      setDownloading(null);
    }
  }

  const lastChecked = dataUpdatedAt ? new Date(dataUpdatedAt).toLocaleTimeString() : null;

  return (
    <Layout title="Verification" subtitle="Run a read-only, Ed25519-signed probe on the target host and ingest the result here.">
      <div className="space-y-6">
        <div className="card bg-bg-raised border-accent/20">
          <p className="text-xs text-light/80 leading-relaxed">
            A verification probe has to run <strong className="text-accent-ink">on the machine itself</strong> to check
            things like firewall state, antivirus, and disk encryption — a web page in your browser is deliberately
            blocked from reading any of that, for the same security reasons this check matters. So there's one
            unavoidable step: paste the command below into a terminal on the machine you want checked. Everything
            else — the assessment ID, your token, submitting the result — is handled for you.
          </p>
        </div>

        <div className="card">
          <div className="label-text mb-3">1. Copy your ready-to-run command</div>
          <div className="flex gap-2 mb-3">
            <button
              className={`px-3 py-1.5 rounded-md text-xs font-medium border transition-colors ${platform === "powershell" ? "bg-accent border-accent text-ink" : "border-border text-light hover:border-accent"}`}
              onClick={() => setPlatform("powershell")}
            >
              Windows (PowerShell)
            </button>
            <button
              className={`px-3 py-1.5 rounded-md text-xs font-medium border transition-colors ${platform === "bash" ? "bg-accent border-accent text-ink" : "border-border text-light hover:border-accent"}`}
              onClick={() => setPlatform("bash")}
            >
              Linux / macOS (Bash)
            </button>
          </div>

          <pre className="bg-bg-raised border border-border rounded-md p-3 text-[11px] text-light overflow-x-auto whitespace-pre-wrap break-all">{command}</pre>

          <div className="flex items-center gap-3 mt-3">
            <button className="btn-primary text-xs" onClick={copyCommand}>
              {commandCopied ? "Copied!" : "Copy command"}
            </button>
            <button
              className="text-xs text-muted hover:text-accent-ink underline decoration-dotted"
              onClick={() => handleDownload(platform)}
              disabled={downloading !== null}
            >
              {downloading === platform ? "Downloading…" : `or download the ${platform === "powershell" ? ".ps1" : ".sh"} script first to inspect it`}
            </button>
          </div>
          {downloadError && <p className="text-[11px] text-red-400 mt-2">{downloadError}</p>}

          <p className="text-[11px] text-muted mt-4 leading-relaxed">
            The command above fetches the script fresh and runs it immediately — no separate download or folder to
            navigate to. It needs OpenSSL on PATH (≥3.0) for the Ed25519 signing step
            {platform === "powershell" ? (
              <> (Windows: <code className="text-accent-ink">winget install ShiningLight.OpenSSL.Light</code>).
              If your machine blocks running local scripts entirely, run <code className="text-accent-ink">Set-ExecutionPolicy -Scope Process -Bypass</code> once first, then paste the command again.</>
            ) : (
              <>.</>
            )}
            {" "}Prefer to read the script before running it? Use the link below instead — that download
            {platform === "powershell" ? " needs one manual Unblock-File step, since browser downloads are flagged by Windows." : " needs chmod +x before it will run."}
          </p>
          <p className="text-[11px] text-muted mt-2">
            A valid signature proves this output came from the official RRI probe script — it does not prove the
            machine itself was uncompromised before the script ran.
          </p>
        </div>

        <div>
          <div className="flex items-center gap-2 mb-3">
            <div className="label-text">2. Results</div>
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-60"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-accent"></span>
            </span>
            <span className="text-[10px] text-muted">
              watching for new results{lastChecked ? ` · last checked ${lastChecked}` : ""}
            </span>
          </div>
          {!runs?.length ? (
            <EmptyState
              title="No probe results yet"
              description="Run the command above from a terminal — this page updates on its own within a few seconds of a submission, no refresh needed."
            />
          ) : (
            <ProbeStatus runs={runs} />
          )}
        </div>
      </div>
    </Layout>
  );
}
