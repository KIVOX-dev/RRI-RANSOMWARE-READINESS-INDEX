import { useBenchmark } from "@/api/hooks";
import { BenchmarkCard } from "@/components/BenchmarkCard";
import { Layout } from "@/components/Layout";
import { useOrganisation } from "@/api/hooks";

export default function Benchmarking() {
  const { data: org } = useOrganisation();
  const { data: benchmark, isLoading } = useBenchmark(org?.id);

  return (
    <Layout title="Sector Benchmarking" subtitle="Compares your organisation against others in the same sector cohort.">
      {isLoading || !benchmark ? <p className="text-sm text-muted">Loading…</p> : <BenchmarkCard benchmark={benchmark} />}
    </Layout>
  );
}
