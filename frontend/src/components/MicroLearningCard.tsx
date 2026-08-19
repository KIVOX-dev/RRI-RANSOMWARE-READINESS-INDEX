import { useState } from "react";
import { useAssistAvailable } from "@/api/hooks";
import { AssistAPI } from "@/api/client";
import type { MicroLearning } from "@/types";

export function MicroLearningCard({ content }: { content: MicroLearning }) {
  const [open, setOpen] = useState(false);
  const { data: assist } = useAssistAvailable();
  const [explanation, setExplanation] = useState<string | null>(null);
  const [explaining, setExplaining] = useState(false);

  async function handleExplain() {
    setExplaining(true);
    try {
      const res = await AssistAPI.explain(`${content.why_it_matters} ${content.good_practice}`);
      setExplanation(res.explanation ?? null);
    } finally {
      setExplaining(false);
    }
  }

  return (
    <div className="border border-border rounded-md bg-bg-raised overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-4 py-2.5 text-xs text-accent-ink hover:bg-bg-card transition-colors"
      >
        <span>Why does this matter?</span>
        <span>{open ? "−" : "+"}</span>
      </button>
      {open && (
        <div className="px-4 pb-4 pt-1 space-y-2.5 text-xs text-light/80 leading-relaxed">
          <p>{content.why_it_matters}</p>
          <div>
            <div className="text-muted uppercase tracking-wide text-[10px] mb-0.5">Risk addressed</div>
            <p>{content.risk_addressed}</p>
          </div>
          <div>
            <div className="text-muted uppercase tracking-wide text-[10px] mb-0.5">Good practice</div>
            <p>{content.good_practice}</p>
          </div>
          <div>
            <div className="text-muted uppercase tracking-wide text-[10px] mb-0.5">Evidence that could support this</div>
            <p>{content.evidence_hint}</p>
          </div>
          {assist?.available && (
            <div className="pt-2 border-t border-border">
              <button className="text-accent-ink text-[11px]" onClick={handleExplain} disabled={explaining}>
                {explaining ? "Explaining…" : "Explain in plain language"}
              </button>
              {explanation && <p className="mt-2 text-light/70 italic">{explanation}</p>}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
