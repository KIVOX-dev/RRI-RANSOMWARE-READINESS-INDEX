import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAssessments, useOrganisation, useStartAssessment } from "@/api/hooks";
import { Layout } from "@/components/Layout";
import { ScoreCard } from "@/components/ScoreCard";
import { apiErrorMessage } from "@/lib/api";
import { useCurrentAssessmentId } from "@/lib/currentAssessment";
import type { AssessmentMode, RoleName } from "@/types";

const ROLES: { value: RoleName; label: string }[] = [
  { value: "executive", label: "Executive" },
  { value: "it_administrator", label: "IT Administrator" },
  { value: "generalist", label: "Generalist" },
];

const MODES: { value: AssessmentMode; label: string; description: string }[] = [
  { value: "basic", label: "Basic track", description: "~24 plain-language questions. A fast readiness snapshot for non-technical users." },
  { value: "full", label: "Full assessment", description: "The complete control catalogue for your sector and role, in impact-ordered rounds." },
];

export default function Overview() {
  const navigate = useNavigate();
  const { data: org } = useOrganisation();
  const { data: assessments, isLoading } = useAssessments();
  const { assessmentId, setCurrentAssessmentId } = useCurrentAssessmentId();
  const startAssessment = useStartAssessment();
  const [role, setRole] = useState<RoleName>("it_administrator");
  const [language, setLanguage] = useState<"en" | "hi">("en");
  const [mode, setMode] = useState<AssessmentMode>("full");
  const [error, setError] = useState<string | null>(null);

  const current = assessments?.find((a) => a.id === assessmentId);
  const inProgress = assessments?.filter((a) => a.status !== "completed") ?? [];
  const completed = assessments?.filter((a) => a.status === "completed") ?? [];

  async function handleStart() {
    if (!org) return;
    setError(null);
    try {
      const assessment = await startAssessment.mutateAsync({ sector: org.sector, role, language, mode });
      setCurrentAssessmentId(assessment.id);
      navigate("/assessment");
    } catch (e) {
      setError(apiErrorMessage(e));
    }
  }

  return (
    <Layout title="Overview" subtitle={org ? `${org.name} · ${org.sector}` : undefined}>
      <div className="space-y-6">
        {current && (
          <div className="card border-accent/40">
            <div className="label-text">Active assessment</div>
            <div className="flex items-center justify-between mt-2">
              <div>
                <div className="text-light">
                  {current.sector} · {current.role.replace("_", " ")} · {current.mode === "basic" ? "Basic track" : "Full"} · {current.status.replace("_", " ")}
                </div>
                <div className="text-xs text-muted mt-1">{current.answered_controls}/{current.total_controls} controls answered</div>
              </div>
              <button className="btn-primary" onClick={() => navigate("/assessment")}>
                {current.status === "completed" ? "Review" : "Continue"}
              </button>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <h2 className="text-light font-medium mb-1">Start a new assessment</h2>
            <p className="text-xs text-muted mb-4">
              Sector is set from your organisation profile ({org?.sector}). Choose the track, role lens, and
              language for this assessment run.
            </p>
            <div className="space-y-3">
              <div>
                <label className="label-text">Track</label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-1">
                  {MODES.map((m) => (
                    <button
                      key={m.value}
                      type="button"
                      onClick={() => setMode(m.value)}
                      className={`text-left px-3 py-2.5 rounded-md border transition-colors ${
                        mode === m.value ? "border-accent bg-accent/10" : "border-border hover:border-accent/60"
                      }`}
                    >
                      <div className={`text-sm font-medium ${mode === m.value ? "text-accent-ink" : "text-light"}`}>{m.label}</div>
                      <div className="text-[11px] text-muted mt-0.5 leading-snug">{m.description}</div>
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="label-text">Role</label>
                <select className="input-field mt-1" value={role} onChange={(e) => setRole(e.target.value as RoleName)}>
                  {ROLES.map((r) => (
                    <option key={r.value} value={r.value}>{r.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="label-text">Language</label>
                <select className="input-field mt-1" value={language} onChange={(e) => setLanguage(e.target.value as "en" | "hi")}>
                  <option value="en">English</option>
                  <option value="hi">हिन्दी</option>
                </select>
              </div>
              {error && <p className="text-xs text-red-400">{error}</p>}
              <button className="btn-primary w-full" onClick={handleStart} disabled={startAssessment.isPending}>
                {startAssessment.isPending ? "Starting…" : "Start assessment"}
              </button>
            </div>
          </div>

          <div className="card">
            <h2 className="text-light font-medium mb-3">Your assessments</h2>
            {isLoading && <p className="text-xs text-muted">Loading…</p>}
            {!isLoading && !assessments?.length && <p className="text-xs text-muted">No assessments started yet.</p>}
            <div className="space-y-2 max-h-72 overflow-y-auto">
              {assessments?.map((a) => (
                <button
                  key={a.id}
                  onClick={() => {
                    setCurrentAssessmentId(a.id);
                    navigate(a.status === "completed" ? "/dashboard" : "/assessment");
                  }}
                  className="w-full flex items-center justify-between px-3 py-2.5 rounded-md border border-border hover:border-accent transition-colors text-left"
                >
                  <div>
                    <div className="text-sm text-light">{a.sector} · {a.role.replace("_", " ")} · {a.mode === "basic" ? "Basic" : "Full"}</div>
                    <div className="text-[10px] text-muted uppercase tracking-wide">{a.status.replace("_", " ")}</div>
                  </div>
                  {a.status === "completed" && (
                    <div className="text-right text-xs">
                      <div className="text-accent-ink font-medium">{a.maturity_score?.toFixed(1)}/5</div>
                      <div className="text-muted">{a.assurance_score?.toFixed(0)}% assured</div>
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>
        </div>

        {completed.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <ScoreCard label="Completed Assessments" value={completed.length} />
            <ScoreCard label="In Progress" value={inProgress.length} />
            <ScoreCard
              label="Latest Maturity"
              value={completed[0]?.maturity_score?.toFixed(1) ?? "—"}
              suffix="/5"
              accent
            />
          </div>
        )}
      </div>
    </Layout>
  );
}
