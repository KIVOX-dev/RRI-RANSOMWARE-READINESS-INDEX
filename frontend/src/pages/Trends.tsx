import { useOrganisation, useTrends } from "@/api/hooks";
import { Layout } from "@/components/Layout";
import { TrendChart } from "@/components/TrendChart";

export default function Trends() {
  const { data: org } = useOrganisation();
  const { data: trend, isLoading } = useTrends(org?.id);

  return (
    <Layout title="Trend Analytics" subtitle="Maturity and Assurance across completed assessments over time.">
      <div className="card">
        {isLoading || !trend ? <p className="text-sm text-muted">Loading…</p> : <TrendChart trend={trend} />}
      </div>
    </Layout>
  );
}
