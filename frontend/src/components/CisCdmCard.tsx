import { useState } from "react";
import type { CisCdmReference } from "@/types";

export function CisCdmCard({ content }: { content: CisCdmReference }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="border border-border rounded-md bg-bg-raised overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-4 py-2.5 text-xs text-accent-ink hover:bg-bg-card transition-colors"
      >
        <span>Why this weight? (CIS Community Defense Model)</span>
        <span>{open ? "−" : "+"}</span>
      </button>
      {open && (
        <div className="px-4 pb-4 pt-1 space-y-3 text-xs text-light/80 leading-relaxed">
          {content.safeguards.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {content.safeguards.map((sg) => (
                <span key={sg.id} className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-bg-card border border-border text-muted">
                  CIS {sg.id} · {sg.ig}
                  {typeof sg.technique_count === "number" && <> · {sg.technique_count} ATT&CK techniques</>}
                </span>
              ))}
            </div>
          ) : (
            <div className="text-[10px] text-muted uppercase tracking-wide">Foundational — not ATT&CK-mapped by CDM</div>
          )}
          <p>{content.note}</p>
          <a href={content.source_url} target="_blank" rel="noreferrer" className="text-accent-ink text-[11px] underline">
            {content.source_title}
          </a>
        </div>
      )}
    </div>
  );
}
