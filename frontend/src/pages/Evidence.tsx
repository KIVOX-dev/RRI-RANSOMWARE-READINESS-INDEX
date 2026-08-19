import { useState } from "react";
import { useAssessment, useDeleteEvidence, useEvidence, useQuestions, useRejectEvidence, useVerifyEvidence } from "@/api/hooks";
import { EmptyState } from "@/components/EmptyState";
import { EvidenceUploader } from "@/components/EvidenceUploader";
import { Layout } from "@/components/Layout";
import { useAuth } from "@/lib/auth";
import { useCurrentAssessmentId } from "@/lib/currentAssessment";

const STATUS_STYLES: Record<string, string> = {
  verified: "text-accent-ink",
  rejected: "text-red-400",
  pending: "text-muted",
};

export default function Evidence() {
  const { user } = useAuth();
  const { assessmentId } = useCurrentAssessmentId();
  const { data: assessment } = useAssessment(assessmentId ?? undefined);
  const { data: questions } = useQuestions(assessment?.sector, assessment?.role, assessment?.language);
  const { data: evidence } = useEvidence(assessmentId ?? undefined);
  const deleteEvidence = useDeleteEvidence(assessmentId ?? "");
  const verifyEvidence = useVerifyEvidence(assessmentId ?? "");
  const rejectEvidence = useRejectEvidence(assessmentId ?? "");
  const [selectedControl, setSelectedControl] = useState<string | null>(null);
  const canReview = user?.role === "platform_admin";

  if (!assessmentId) {
    return (
      <Layout title="Evidence">
        <EmptyState title="No active assessment" description="Start an assessment from the Overview page first." />
      </Layout>
    );
  }

  const evidenceByControl = new Map<string, typeof evidence>();
  evidence?.forEach((e) => {
    evidenceByControl.set(e.control_id, [...(evidenceByControl.get(e.control_id) ?? []), e]);
  });

  return (
    <Layout title="Evidence" subtitle="Evidence you upload directly raises the Assurance Score for the associated control.">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-2">
          {questions?.filter((q) => q.evidence_required).map((q) => {
            const items = evidenceByControl.get(q.control_id) ?? [];
            return (
              <div key={q.id} className="card">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm text-light">{q.title}</div>
                    <div className="text-[10px] text-muted uppercase tracking-wide mt-0.5">{q.domain} · {q.control_id}</div>
                  </div>
                  <button className="btn-secondary text-xs" onClick={() => setSelectedControl(selectedControl === q.control_id ? null : q.control_id)}>
                    {selectedControl === q.control_id ? "Close" : "Upload"}
                  </button>
                </div>

                {items.length > 0 && (
                  <div className="mt-3 space-y-1.5">
                    {items.map((ev) => (
                      <div key={ev.id} className="flex items-center justify-between text-xs bg-bg-raised rounded px-3 py-2">
                        <div>
                          <span className="text-light">{ev.filename}</span>
                          <span className={`ml-2 uppercase text-[10px] ${STATUS_STYLES[ev.verification_status] ?? "text-muted"}`}>
                            {ev.verification_status}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          {ev.download_url && (
                            <a href={ev.download_url} target="_blank" rel="noreferrer" className="text-accent-ink">View</a>
                          )}
                          {canReview && ev.verification_status === "pending" && (
                            <>
                              <button
                                className="text-accent-ink"
                                disabled={verifyEvidence.isPending}
                                onClick={() => verifyEvidence.mutate(ev.id)}
                              >
                                Verify
                              </button>
                              <button
                                className="text-red-400"
                                disabled={rejectEvidence.isPending}
                                onClick={() => rejectEvidence.mutate(ev.id)}
                              >
                                Reject
                              </button>
                            </>
                          )}
                          <button className="text-red-400" onClick={() => deleteEvidence.mutate(ev.id)}>Delete</button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {selectedControl === q.control_id && (
                  <div className="mt-3">
                    <EvidenceUploader assessmentId={assessmentId} controlId={q.control_id} />
                  </div>
                )}
              </div>
            );
          })}
          {questions && questions.filter((q) => q.evidence_required).length === 0 && (
            <EmptyState title="No controls require evidence" description="None of the routed controls for this assessment are flagged as evidence-required." />
          )}
        </div>

        <div className="card h-fit">
          <div className="label-text mb-2">Retention policy</div>
          <p className="text-xs text-light/70 leading-relaxed">
            Evidence files are stored securely in object storage and linked only to your organisation's assessment.
            Files can be removed at any time using the Delete action, which also recalculates your Assurance Score.
          </p>
        </div>
      </div>
    </Layout>
  );
}
