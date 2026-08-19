import { PolarAngleAxis, PolarGrid, PolarRadiusAxis, Radar, RadarChart, ResponsiveContainer, Tooltip } from "recharts";
import type { DomainScore } from "@/types";
import { EmptyState } from "@/components/EmptyState";
import { chartTheme } from "@/lib/chartTheme";

export function MaturityRadar({ domainScores }: { domainScores: DomainScore[] }) {
  if (!domainScores.length) {
    return <EmptyState title="No domain scores yet" description="Answer assessment questions to populate the maturity radar." />;
  }

  const data = domainScores.map((d) => ({ domain: d.domain, score: d.maturity_score }));

  return (
    <ResponsiveContainer width="100%" height={340}>
      <RadarChart data={data} outerRadius="70%">
        <PolarGrid stroke={chartTheme.grid} />
        <PolarAngleAxis dataKey="domain" tick={{ fill: chartTheme.tick, fontSize: 10 }} />
        <PolarRadiusAxis angle={30} domain={[0, 5]} tick={{ fill: chartTheme.mutedTick, fontSize: 10 }} />
        <Radar name="Maturity" dataKey="score" stroke={chartTheme.accent} fill={chartTheme.accent} fillOpacity={0.35} />
        <Tooltip
          contentStyle={{ background: chartTheme.tooltipBg, border: `1px solid ${chartTheme.tooltipBorder}`, borderRadius: 8, color: chartTheme.ink }}
          formatter={(value: number) => [`${value} / 5`, "Maturity"]}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
}
