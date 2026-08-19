import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts";
import { chartTheme } from "@/lib/chartTheme";

export function AssuranceGauge({ assuranceScore }: { assuranceScore: number }) {
  const value = Math.max(0, Math.min(100, assuranceScore ?? 0));
  const data = [
    { name: "assured", value },
    { name: "remaining", value: 100 - value },
  ];

  return (
    <div className="relative w-full flex flex-col items-center">
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            startAngle={90}
            endAngle={-270}
            innerRadius="70%"
            outerRadius="95%"
            stroke="none"
          >
            <Cell fill={chartTheme.accent} />
            <Cell fill={chartTheme.track} />
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <div className="text-3xl font-bold text-accent-ink">{value.toFixed(0)}%</div>
        <div className="label-text mt-1">Assurance</div>
      </div>
    </div>
  );
}
