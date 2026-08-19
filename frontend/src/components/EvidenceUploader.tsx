import { useRef, useState } from "react";
import { useUploadEvidence } from "@/api/hooks";
import { apiErrorMessage } from "@/lib/api";

export function EvidenceUploader({ assessmentId, controlId }: { assessmentId: string; controlId: string }) {
  const upload = useUploadEvidence(assessmentId);
  const [progress, setProgress] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  function handleFile(file: File) {
    setError(null);
    setProgress(0);
    upload.mutate(
      { controlId, file, onProgress: setProgress },
      {
        onError: (e) => setError(apiErrorMessage(e)),
        onSettled: () => setProgress(null),
      }
    );
  }

  return (
    <div className="border border-dashed border-border rounded-md p-4 text-center">
      <input
        ref={inputRef}
        type="file"
        className="hidden"
        onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
        accept=".pdf,.png,.jpg,.jpeg,.docx,.xlsx,.txt,.csv,.json"
      />
      <button className="btn-secondary text-xs" onClick={() => inputRef.current?.click()} disabled={upload.isPending}>
        {upload.isPending ? `Uploading… ${progress ?? 0}%` : "Upload evidence"}
      </button>
      <p className="text-[10px] text-muted mt-2">PDF, image, Office, text, or JSON · up to 25MB</p>
      {error && <p className="text-[11px] text-red-400 mt-2">{error}</p>}
    </div>
  );
}
