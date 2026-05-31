import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "components/ui/card";
import { MetricChart } from "features/dashboard/types";

function Sparkline({ points }: { points: number[] }) {
  const max = Math.max(...points);

  return (
    <div className="mt-5 flex h-32 items-end gap-1.5">
      {points.map((point, index) => (
        <div key={`${point}-${index}`} className="flex-1 rounded-t-2xl bg-cyan-400/15">
          <div
            className="w-full rounded-t-2xl bg-gradient-to-t from-cyan-500/40 to-cyan-300/90"
            style={{ height: `${Math.max((point / max) * 100, 16)}%` }}
          />
        </div>
      ))}
    </div>
  );
}

export function MetricsCharts({ charts }: { charts: MetricChart[] }) {
  return (
    <section className="grid gap-4 md:grid-cols-2 2xl:grid-cols-3">
      {charts.map((chart) => (
        <Card key={chart.id}>
          <CardHeader>
            <CardDescription>Metrics placeholder</CardDescription>
            <div className="flex items-start justify-between gap-4">
              <CardTitle>{chart.title}</CardTitle>
              <span className="rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs text-emerald-200">{chart.change}</span>
            </div>
          </CardHeader>
          <CardContent>
            <Sparkline points={chart.points} />
            <div className="mt-4 flex items-center justify-between text-xs uppercase tracking-[0.22em] text-slate-500">
              <span>-45m</span>
              <span>Now</span>
            </div>
          </CardContent>
        </Card>
      ))}
    </section>
  );
}
