import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useBackup, useUpsertBackup } from "@/api/hooks";
import { EmptyState } from "@/components/EmptyState";
import { Layout } from "@/components/Layout";
import { useCurrentAssessmentId } from "@/lib/currentAssessment";

const schema = z.object({
  backup_destination: z.string().min(1, "Required"),
  is_writable_from_production: z.boolean(),
  backup_frequency: z.string().min(1, "Required"),
  last_successful_backup: z.string().optional(),
  last_restore_test: z.string().optional(),
  restore_test_owner: z.string().optional(),
  recovery_confidence: z.coerce.number().min(1).max(5),
});
type FormValues = z.infer<typeof schema>;

export default function BackupResiliencePage() {
  const { assessmentId } = useCurrentAssessmentId();
  const { data: backup } = useBackup(assessmentId ?? undefined);
  const upsert = useUpsertBackup(assessmentId ?? "");
  const { register, handleSubmit, reset } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { is_writable_from_production: false, recovery_confidence: 3 },
  });

  useEffect(() => {
    if (backup) reset(backup as unknown as FormValues);
  }, [backup, reset]);

  if (!assessmentId) {
    return (
      <Layout title="Backup Resilience">
        <EmptyState title="No active assessment" description="Start an assessment from the Overview page first." />
      </Layout>
    );
  }

  return (
    <Layout title="Backup Resilience Deep-Dive" subtitle="Missing restore testing is treated as a high-priority remediation gap.">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <form className="card space-y-3" onSubmit={handleSubmit((v) => upsert.mutate(v))}>
          <div>
            <label className="label-text" htmlFor="backup_destination">Backup destination</label>
            <input id="backup_destination" className="input-field mt-1" {...register("backup_destination")} placeholder="e.g. offsite object storage, tape vault" />
          </div>
          <label className="flex items-center gap-2 text-xs text-muted">
            <input type="checkbox" {...register("is_writable_from_production")} />
            Writable directly from production accounts
          </label>
          <div>
            <label className="label-text" htmlFor="backup_frequency">Backup frequency</label>
            <input id="backup_frequency" className="input-field mt-1" {...register("backup_frequency")} placeholder="e.g. daily, hourly" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label-text" htmlFor="last_successful_backup">Last successful backup</label>
              <input id="last_successful_backup" type="date" className="input-field mt-1" {...register("last_successful_backup")} />
            </div>
            <div>
              <label className="label-text" htmlFor="last_restore_test">Last restore test</label>
              <input id="last_restore_test" type="date" className="input-field mt-1" {...register("last_restore_test")} />
            </div>
          </div>
          <div>
            <label className="label-text" htmlFor="restore_test_owner">Restore-test owner</label>
            <input id="restore_test_owner" className="input-field mt-1" {...register("restore_test_owner")} />
          </div>
          <div>
            <label className="label-text" htmlFor="recovery_confidence">Recovery confidence (1-5)</label>
            <input id="recovery_confidence" type="number" min={1} max={5} className="input-field mt-1" {...register("recovery_confidence")} />
          </div>
          <button className="btn-primary w-full" disabled={upsert.isPending}>
            {upsert.isPending ? "Saving…" : "Save"}
          </button>
        </form>

        <div className="space-y-4">
          {backup ? (
            <div className={`card ${backup.restore_test_gap ? "border-red-500/40" : "border-accent/40"}`}>
              <div className="label-text mb-2">Risk Assessment</div>
              <p className={`text-sm ${backup.restore_test_gap ? "text-red-400" : "text-accent-ink"}`}>{backup.risk_note}</p>
            </div>
          ) : (
            <EmptyState title="No backup data recorded" description="Fill in the form to capture your backup resilience posture." />
          )}
        </div>
      </div>
    </Layout>
  );
}
