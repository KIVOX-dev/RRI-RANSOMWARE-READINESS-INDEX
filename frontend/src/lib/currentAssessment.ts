import { useCallback, useEffect, useState } from "react";

const KEY = "rri_current_assessment_id";

export function useCurrentAssessmentId() {
  const [id, setId] = useState<string | null>(() => localStorage.getItem(KEY));

  useEffect(() => {
    function onStorage() {
      setId(localStorage.getItem(KEY));
    }
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);

  const setCurrentAssessmentId = useCallback((value: string | null) => {
    if (value) localStorage.setItem(KEY, value);
    else localStorage.removeItem(KEY);
    setId(value);
  }, []);

  return { assessmentId: id, setCurrentAssessmentId };
}
