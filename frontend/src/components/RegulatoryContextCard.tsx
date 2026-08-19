import { useState } from "react";
import type { RegulatoryContext } from "@/types";

export function RegulatoryContextCard({ content }: { content: RegulatoryContext }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="border border-border rounded-md bg-bg-raised overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-4 py-2.5 text-xs text-accent-ink hover:bg-bg-card transition-colors"
      >
        <span>India regulatory context</span>
        <span>{open ? "−" : "+"}</span>
      </button>
      {open && (
        <div className="px-4 pb-4 pt-1 space-y-3 text-xs text-light/80 leading-relaxed">
          {content.references.map((ref, i) => (
            <div key={i}>
              <div className="text-muted uppercase tracking-wide text-[10px] mb-0.5">{ref.framework}</div>
              <p>{ref.note}</p>
              {ref.url && (
                <a href={ref.url} target="_blank" rel="noreferrer" className="text-accent-ink text-[11px] underline">
                  {ref.url}
                </a>
              )}
            </div>
          ))}
          <p className="text-[10px] text-muted italic pt-2 border-t border-border">{content.disclaimer}</p>
        </div>
      )}
    </div>
  );
}
