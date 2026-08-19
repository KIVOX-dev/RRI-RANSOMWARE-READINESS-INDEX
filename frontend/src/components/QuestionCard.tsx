import { motion } from "framer-motion";
import { useState } from "react";
import { CisCdmCard } from "@/components/CisCdmCard";
import { MicroLearningCard } from "@/components/MicroLearningCard";
import { RegulatoryContextCard } from "@/components/RegulatoryContextCard";
import type { Question } from "@/types";

const IMPACT_STYLES: Record<string, string> = {
  high: "bg-red-500/15 text-red-400 border-red-500/40",
  medium: "bg-accent/15 text-accent-ink border-accent/40",
  low: "bg-bg-raised text-muted border-border",
};

export function QuestionCard({
  question,
  value,
  onAnswer,
  saving,
}: {
  question: Question;
  value: unknown;
  onAnswer: (value: unknown) => void;
  saving: boolean;
}) {
  const [text, setText] = useState(typeof value === "string" ? value : "");

  return (
    <motion.div
      key={question.id}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="card max-w-2xl"
    >
      <div className="flex items-center gap-2 mb-3">
        <span className="text-[10px] text-muted uppercase tracking-wider">{question.domain}</span>
        <span className={`text-[10px] px-2 py-0.5 rounded border uppercase ${IMPACT_STYLES[question.impact_level]}`}>
          {question.impact_level} impact
        </span>
        {saving && <span className="text-[10px] text-accent-ink ml-auto">Saving…</span>}
      </div>

      <h2 className="text-lg text-light font-medium leading-snug">{question.title}</h2>
      {question.description && <p className="text-sm text-muted mt-2">{question.description}</p>}

      <div className="mt-5 space-y-2">
        {question.answer_type === "boolean" && (
          <div className="flex gap-3">
            <button
              onClick={() => onAnswer(true)}
              className={`flex-1 py-2.5 rounded-md border text-sm font-medium transition-colors ${
                value === true ? "bg-accent text-ink border-accent" : "border-border text-light hover:border-accent"
              }`}
            >
              Yes
            </button>
            <button
              onClick={() => onAnswer(false)}
              className={`flex-1 py-2.5 rounded-md border text-sm font-medium transition-colors ${
                value === false ? "bg-accent text-ink border-accent" : "border-border text-light hover:border-accent"
              }`}
            >
              No
            </button>
          </div>
        )}

        {question.answer_type === "scale" && (
          <div className="flex gap-2">
            {[0, 1, 2, 3, 4, 5].map((n) => (
              <button
                key={n}
                onClick={() => onAnswer(n)}
                className={`flex-1 py-2.5 rounded-md border text-sm font-medium transition-colors ${
                  value === n ? "bg-accent text-ink border-accent" : "border-border text-light hover:border-accent"
                }`}
              >
                {n}
              </button>
            ))}
          </div>
        )}

        {(question.answer_type === "single_select" || question.answer_type === "multi_select") && (
          <div className="space-y-2">
            {question.options.map((opt) => {
              const selected =
                question.answer_type === "single_select" ? value === opt.value : Array.isArray(value) && value.includes(opt.value);
              return (
                <button
                  key={opt.value}
                  onClick={() => {
                    if (question.answer_type === "single_select") {
                      onAnswer(opt.value);
                    } else {
                      const arr = Array.isArray(value) ? [...(value as string[])] : [];
                      const next = arr.includes(opt.value) ? arr.filter((v) => v !== opt.value) : [...arr, opt.value];
                      onAnswer(next);
                    }
                  }}
                  className={`w-full text-left px-4 py-2.5 rounded-md border text-sm transition-colors ${
                    selected ? "bg-accent text-ink border-accent" : "border-border text-light hover:border-accent"
                  }`}
                >
                  {opt.label}
                </button>
              );
            })}
          </div>
        )}

        {question.answer_type === "text" && (
          <div className="flex gap-2">
            <input
              className="input-field"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Type your answer…"
            />
            <button className="btn-primary" onClick={() => onAnswer(text)} disabled={!text.trim()}>
              Save
            </button>
          </div>
        )}
      </div>

      {question.micro_learning && (
        <div className="mt-5">
          <MicroLearningCard content={question.micro_learning} />
        </div>
      )}

      {question.regulatory_context && (
        <div className="mt-3">
          <RegulatoryContextCard content={question.regulatory_context} />
        </div>
      )}

      {question.cis_cdm_reference && (
        <div className="mt-3">
          <CisCdmCard content={question.cis_cdm_reference} />
        </div>
      )}

      {question.evidence_required && (
        <p className="text-[11px] text-accent-ink mt-4">Evidence recommended for this control — upload it from the Evidence page.</p>
      )}
    </motion.div>
  );
}
