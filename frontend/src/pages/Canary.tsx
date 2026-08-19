import { useEffect, useState } from "react";
import { CanaryAPI } from "@/api/client";
import { useCanaries, useCanaryEvents, useDeployCanaries, useSimulateCanary } from "@/api/hooks";
import { CanaryAlert } from "@/components/CanaryAlert";
import { EmptyState } from "@/components/EmptyState";
import { Layout } from "@/components/Layout";
import { getToken } from "@/lib/api";
import { useCurrentAssessmentId } from "@/lib/currentAssessment";
import type { CanaryEvent } from "@/types";

export default function Canary() {
  const { assessmentId } = useCurrentAssessmentId();
  const { data: canaries } = useCanaries();
  const { data: events } = useCanaryEvents();
  const deploy = useDeployCanaries();
  const simulate = useSimulateCanary();
  const [liveEvents, setLiveEvents] = useState<CanaryEvent[]>([]);

  useEffect(() => {
    const token = getToken();
    if (!token) return;
    const source = new EventSource(CanaryAPI.streamUrl(token));
    source.addEventListener("canary_event", (e) => {
      try {
        const event = JSON.parse((e as MessageEvent).data);
        setLiveEvents((prev) => [event, ...prev].slice(0, 20));
      } catch {
        /* ignore malformed event */
      }
    });
    return () => source.close();
  }, []);

  const allEvents = [...liveEvents, ...(events ?? [])].filter(
    (e, idx, arr) => arr.findIndex((x) => x.id === e.id) === idx
  );

  return (
    <Layout
      title="Canary Tripwire"
      subtitle="Decoy files deployed on the backend host, watched by a simulated local tripwire — real events, clearly labeled."
    >
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div className="card">
            <div className="flex items-center justify-between">
              <div className="label-text">Deployed canaries</div>
              <button
                className="btn-primary text-xs"
                onClick={() => deploy.mutate({ count: 5, assessmentId: assessmentId ?? undefined })}
                disabled={deploy.isPending}
              >
                {deploy.isPending ? "Deploying…" : "Deploy 5 canaries"}
              </button>
            </div>
            <div className="mt-3 space-y-2">
              {!canaries?.length && <p className="text-xs text-muted">No canaries deployed yet.</p>}
              {canaries?.map((c) => (
                <div key={c.id} className="flex items-center justify-between bg-bg-raised rounded px-3 py-2 text-xs">
                  <div>
                    <div className="text-light">{c.file_path.split(/[/\\]/).pop()}</div>
                    <div className="text-muted uppercase text-[10px] mt-0.5">{c.status}</div>
                  </div>
                  <button
                    className="text-accent-ink disabled:opacity-40"
                    onClick={() => simulate.mutate(c.canary_id)}
                    disabled={simulate.isPending || c.status === "tripped"}
                  >
                    Simulate touch
                  </button>
                </div>
              ))}
            </div>
          </div>
          <p className="text-[11px] text-muted leading-relaxed">
            "Simulate touch" is a demo-only action that intentionally modifies a decoy file so you can see the
            tripwire fire immediately, instead of waiting for the background watcher's next poll cycle.
          </p>
        </div>

        <div>
          <div className="label-text mb-3">Live events</div>
          {!allEvents.length ? (
            <EmptyState title="No canary events yet" description="Deploy canaries and simulate a touch to see a live event appear here." />
          ) : (
            <div className="space-y-2">
              {allEvents.map((e) => (
                <CanaryAlert key={e.id} event={e} />
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
