import { Activity, AlertTriangle, Gauge, Layers3 } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "components/ui/card";
import { DashboardData } from "features/dashboard/types";

const summaryIcons = [Layers3, AlertTriangle, Activity, Gauge];

export function ServiceOverviewGrid({ data }: { data: DashboardData }) {
  const summaryCards = [
    { label: "Monitored services", value: data.summary.monitoredServices, hint: "Across core platform and edge systems" },
    { label: "Open alerts", value: data.summary.openAlerts, hint: "Critical routing prioritized by service tier" },
    { label: "Monthly availability", value: data.summary.monthlyAvailability, hint: "Global availability across all regions" },
    { label: "Last sync", value: data.summary.lastUpdated, hint: "Telemetry stream and alert state updated" },
  ];

  return (
    <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {summaryCards.map((card, index) => {
        const Icon = summaryIcons[index];

        return (
          <Card key={card.label}>
            <CardHeader className="flex-row items-start justify-between space-y-0">
              <div>
                <CardDescription>{card.label}</CardDescription>
                <CardTitle className="mt-3 text-3xl">{card.value}</CardTitle>
              </div>
              <div className="rounded-2xl border border-cyan-400/10 bg-cyan-400/10 p-3 text-cyan-200">
                <Icon className="h-5 w-5" />
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-400">{card.hint}</p>
            </CardContent>
          </Card>
        );
      })}
    </section>
  );
}
