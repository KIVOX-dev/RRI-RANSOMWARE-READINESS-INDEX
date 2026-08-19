import { AnimatePresence } from "framer-motion";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAnswers, useAssessment, useCompleteAssessment, useQuestions, useSubmitAnswer } from "@/api/hooks";
import { AssessmentProgress } from "@/components/AssessmentProgress";
import { EmptyState } from "@/components/EmptyState";
import { Layout } from "@/components/Layout";
import { QuestionCard } from "@/components/QuestionCard";
import { useCurrentAssessmentId } from "@/lib/currentAssessment";

export default function AssessmentFlow() {
  const navigate = useNavigate();
  const { assessmentId } = useCurrentAssessmentId();
  const { data: assessment, isLoading: loadingAssessment } = useAssessment(assessmentId ?? undefined);
  const { data: questions, isLoading: loadingQuestions } = useQuestions(assessment?.sector, assessment?.role, assessment?.language, assessment?.mode);
  const { data: answers } = useAnswers(assessmentId ?? undefined);
  const submitAnswer = useSubmitAnswer(assessmentId ?? "");
  const completeAssessment = useCompleteAssessment(assessmentId ?? "");
  const [index, setIndex] = useState(0);

  const answersByControl = useMemo(() => {
    const map = new Map<string, unknown>();
    answers?.forEach((a) => map.set(a.control_id, a.answer));
    return map;
  }, [answers]);

  useEffect(() => {
    if (questions?.length) {
      const firstUnanswered = questions.findIndex((q) => !answersByControl.has(q.control_id));
      if (firstUnanswered >= 0) setIndex(firstUnanswered);
    }
  }, [questions?.length]); // eslint-disable-line react-hooks/exhaustive-deps

  // Rounds: questions arrive from the backend already grouped in round order
  // (impact-sorted, chunked into rounds of 25), so this just reads the
  // `round` field already on each question rather than re-deriving it.
  const roundCount = questions?.[0]?.round_count ?? 1;
  const questionsByRound = useMemo(() => {
    const map = new Map<number, typeof questions>();
    questions?.forEach((q) => {
      const list = map.get(q.round) ?? [];
      list.push(q);
      map.set(q.round, list);
    });
    return map;
  }, [questions]);

  if (!assessmentId) {
    return (
      <Layout title="Assessment">
        <EmptyState title="No active assessment" description="Start an assessment from the Overview page first." />
      </Layout>
    );
  }

  if (loadingAssessment || loadingQuestions || !assessment || !questions) {
    return (
      <Layout title="Assessment">
        <p className="text-sm text-muted">Loading assessment…</p>
      </Layout>
    );
  }

  const allQuestions = questions;
  const totalQuestions = allQuestions.length;
  const question = allQuestions[index];
  const isLast = index === totalQuestions - 1;
  const currentRound = question?.round ?? 1;
  const currentRoundQuestions = questionsByRound.get(currentRound) ?? [];

  async function handleAnswer(value: unknown) {
    await submitAnswer.mutateAsync({ controlId: question.control_id, answer: value });
    if (!isLast) {
      setTimeout(() => setIndex((i) => Math.min(totalQuestions - 1, i + 1)), 200);
    }
  }

  async function handleComplete() {
    await completeAssessment.mutateAsync();
    navigate("/dashboard");
  }

  function jumpToRound(round: number) {
    const roundQuestions = questionsByRound.get(round) ?? [];
    const firstUnanswered = roundQuestions.findIndex((q) => !answersByControl.has(q.control_id));
    const target = firstUnanswered >= 0 ? roundQuestions[firstUnanswered] : roundQuestions[0];
    if (target) setIndex(allQuestions.findIndex((q) => q.id === target.id));
  }

  const atRoundEnd = index === totalQuestions - 1 || allQuestions[index + 1]?.round !== currentRound;
  const nextRoundExists = currentRound < roundCount;

  return (
    <Layout
      title="Assessment"
      subtitle={`${assessment.sector} · ${assessment.role.replace("_", " ")} · ${assessment.language.toUpperCase()} · ${assessment.mode === "basic" ? "Basic track" : "Full assessment"}`}
    >
      <div className="space-y-6">
        {assessment.mode === "basic" && (
          <div className="card border-accent/40 text-xs text-light/80">
            <span className="text-accent-ink font-medium">Basic track</span> — a short, plain-language set of{" "}
            {allQuestions.length} high-impact questions for a fast readiness snapshot. For the complete control
            catalogue, start a new "Full assessment" from the Overview page instead.
          </div>
        )}

        <AssessmentProgress progress={assessment.progress} answered={assessment.answered_controls} total={assessment.total_controls} />

        {roundCount > 1 && (
          <div>
            <div className="label-text mb-2">Rounds — high-impact controls first, {allQuestions.length} controls total</div>
            <div className="flex gap-2 flex-wrap">
              {Array.from({ length: roundCount }, (_, i) => i + 1).map((round) => {
                const roundQuestions = questionsByRound.get(round) ?? [];
                const answeredInRound = roundQuestions.filter((q) => answersByControl.has(q.control_id)).length;
                const complete = roundQuestions.length > 0 && answeredInRound === roundQuestions.length;
                return (
                  <button
                    key={round}
                    onClick={() => jumpToRound(round)}
                    className={`px-3 py-1.5 rounded-md text-xs font-medium border transition-colors ${
                      round === currentRound
                        ? "bg-accent border-accent text-ink"
                        : complete
                          ? "border-accent/50 text-accent-ink"
                          : "border-border text-light hover:border-accent"
                    }`}
                  >
                    Round {round}
                    <span className="opacity-70 ml-1.5">
                      {complete ? "✓" : `${answeredInRound}/${roundQuestions.length}`}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        <div className="flex gap-2 flex-wrap">
          {currentRoundQuestions.map((q) => {
            const i = allQuestions.findIndex((qq) => qq.id === q.id);
            return (
              <button
                key={q.id}
                onClick={() => setIndex(i)}
                className={`w-2 h-2 rounded-full transition-colors ${
                  i === index ? "bg-accent w-6" : answersByControl.has(q.control_id) ? "bg-accent/50" : "bg-border"
                }`}
                aria-label={`Question ${i + 1}`}
              />
            );
          })}
        </div>

        <AnimatePresence mode="wait">
          {question && (
            <QuestionCard
              key={question.id}
              question={question}
              value={answersByControl.get(question.control_id)}
              onAnswer={handleAnswer}
              saving={submitAnswer.isPending}
            />
          )}
        </AnimatePresence>

        <div className="flex items-center gap-3 max-w-2xl">
          <button className="btn-secondary" onClick={() => setIndex((i) => Math.max(0, i - 1))} disabled={index === 0}>
            Previous
          </button>
          {atRoundEnd && nextRoundExists ? (
            <button className="btn-secondary" onClick={() => jumpToRound(currentRound + 1)}>
              Round {currentRound} done — next round →
            </button>
          ) : (
            <button
              className="btn-secondary"
              onClick={() => setIndex((i) => Math.min(totalQuestions - 1, i + 1))}
              disabled={isLast}
            >
              Skip / Next
            </button>
          )}
          <div className="flex-1" />
          {assessment.status !== "completed" && (
            <button
              className="btn-primary"
              onClick={handleComplete}
              disabled={completeAssessment.isPending || assessment.answered_controls === 0}
            >
              {completeAssessment.isPending ? "Completing…" : "Complete assessment"}
            </button>
          )}
        </div>
      </div>
    </Layout>
  );
}
