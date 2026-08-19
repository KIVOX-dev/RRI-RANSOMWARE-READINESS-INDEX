import { CartesianGrid, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis, ReferenceLine } from "recharts";
import type { RemediationItem } from "@/types";
import { EmptyState } from "@/components/EmptyState";
import { chartTheme } from "@/lib/chartTheme";

const EFFORT_X: Record<string, number> = { low: 25, high: 75 };
const IMPACT_Y: Record<string, number> = { low: 20, medium: 50, high: 85 };

export function RemediationQuadrant({ items }: { items: RemediationItem[] }) {
  if (!items.length) {
    return <EmptyState title="No remediation items" description="Generate the roadmap after answering assessment questions." />;
  }

  const data = items.map((item, idx) => ({
    x: EFFORT_X[item.effort] + (((idx * 7) % 10) - 5),
    y: IMPACT_Y[item.impact] + (((idx * 13) % 10) - 5),
    issue: item.issue,
    priority: item.priority,
  }));

  return (
    <div>
      <ResponsiveContainer width="100%" height={360}>
        <ScatterChart margin={{ top: 20, right: 30, bottom: 20, left: 10 }}>
          <CartesianGrid stroke={chartTheme.grid} />
          <XAxis type="number" dataKey="x" domain={[0, 100]} ticks={[25, 75]} tickFormatter={(v) => (v === 25 ? "Low Effort" : "High Effort")} tick={{ fill: chartTheme.mutedTick, fontSize: 11 }} />
          <YAxis type="number" dataKey="y" domain={[0, 100]} ticks={[20, 85]} tickFormatter={(v) => (v === 20 ? "Low Impact" : "High Impact")} tick={{ fill: chartTheme.mutedTick, fontSize: 11 }} />
          <ReferenceLine x={50} stroke={chartTheme.grid} />
          <ReferenceLine y={50} stroke={chartTheme.grid} />
          <Tooltip
            contentStyle={{ background: chartTheme.tooltipBg, border: `1px solid ${chartTheme.tooltipBorder}`, borderRadius: 8, color: chartTheme.ink }}
            formatter={(_v, _n, entry) => [entry.payload.issue, entry.payload.priority]}
          />
          <Scatter data={data} fill={chartTheme.accent} />
        </ScatterChart>
      </ResponsiveContainer>
      <div className="grid grid-cols-2 text-center text-[10px] text-muted uppercase tracking-wide -mt-2">
        <div>High Impact / Low Effort · High Impact / High Effort</div>
        <div>Low Impact / Low Effort · Low Impact / High Effort</div>
      </div>
    </div>
  );
}
