import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { Trend } from "@/types";
import { EmptyState } from "@/components/EmptyState";
import { chartTheme } from "@/lib/chartTheme";

export function TrendChart({ trend }: { trend: Trend }) {
  if (!trend.available) {
    return <EmptyState title="Not enough history yet" description={trend.message} />;
  }

  const data = trend.points.map((p) => ({
    date: new Date(p.completed_at).toLocaleDateString(),
    Maturity: p.maturity_score,
    Assurance: p.assurance_score,
  }));

  return (
    <ResponsiveContainer width="100%" height={320}>
      <LineChart data={data}>
        <CartesianGrid stroke={chartTheme.grid} />
        <XAxis dataKey="date" tick={{ fill: chartTheme.mutedTick, fontSize: 11 }} />
        <YAxis yAxisId="left" domain={[0, 5]} tick={{ fill: chartTheme.mutedTick, fontSize: 11 }} />
        <YAxis yAxisId="right" orientation="right" domain={[0, 100]} tick={{ fill: chartTheme.mutedTick, fontSize: 11 }} />
        <Tooltip contentStyle={{ background: chartTheme.tooltipBg, border: `1px solid ${chartTheme.tooltipBorder}`, borderRadius: 8, color: chartTheme.ink }} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Line yAxisId="left" type="monotone" dataKey="Maturity" stroke={chartTheme.accent} strokeWidth={2} dot={{ r: 3 }} />
        <Line yAxisId="right" type="monotone" dataKey="Assurance" stroke={chartTheme.ink} strokeWidth={2} dot={{ r: 3 }} />
      </LineChart>
    </ResponsiveContainer>
  );
}
