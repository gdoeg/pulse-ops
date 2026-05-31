import { Badge } from "components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "components/ui/card";
import { DashboardData, ServiceStatus } from "features/dashboard/types";
import { cn } from "lib/utils";

const statusClasses: Record<ServiceStatus, string> = {
  healthy: "bg-emerald-500/10 text-emerald-200",
  degraded: "bg-amber-500/10 text-amber-200",
  critical: "bg-rose-500/10 text-rose-200",
};

export function ServiceStatusPanel({ services }: Pick<DashboardData, "services">) {
  return (
    <Card>
      <CardHeader>
        <CardDescription>Service overview</CardDescription>
        <CardTitle>Tiered service health</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {services.map((service) => (
          <div key={service.name} className="rounded-xl border border-white/5 bg-white/[0.02] p-3">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-medium text-white">{service.name}</h3>
                  <Badge className={cn("border-transparent", statusClasses[service.status])}>{service.status}</Badge>
                </div>
                <p className="mt-1 text-sm text-slate-500">{service.tier}</p>
              </div>
              <div className="text-right text-sm text-slate-400">
                <div>{service.throughput}</div>
                <div>{service.latencyMs}ms p95</div>
              </div>
            </div>
            <div className="mt-3 grid grid-cols-2 gap-2.5 text-sm text-slate-400">
              <div className="rounded-lg bg-slate-900/80 px-2.5 py-2">
                <span className="block text-xs uppercase tracking-[0.18em] text-slate-500">Error rate</span>
                <span className="mt-1 block text-base text-white">{service.errorRate}</span>
              </div>
              <div className="rounded-lg bg-slate-900/80 px-2.5 py-2">
                <span className="block text-xs uppercase tracking-[0.18em] text-slate-500">Throughput</span>
                <span className="mt-1 block text-base text-white">{service.throughput}</span>
              </div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
