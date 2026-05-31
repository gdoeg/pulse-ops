"use client";

import { BellRing } from "lucide-react";
import { useEffect, useState } from "react";

import { Badge } from "components/ui/badge";
import { Button } from "components/ui/button";
import { AutomationEmptyState } from "features/dashboard/components/automation-empty-state";
import { DashboardErrorBoundary } from "features/dashboard/components/dashboard-error-boundary";
import { DashboardLoadingState } from "features/dashboard/components/dashboard-loading-state";
import { DashboardShell } from "features/dashboard/components/dashboard-shell";
import { ErrorMonitoringTable } from "features/dashboard/components/error-monitoring-table";
import { MetricsCharts } from "features/dashboard/components/metrics-charts";
import { ServiceOverviewGrid } from "features/dashboard/components/service-overview-grid";
import { ServiceStatusPanel } from "features/dashboard/components/service-status-panel";
import { UptimeVisualization } from "features/dashboard/components/uptime-visualization";
import { getDashboardData } from "features/dashboard/api/get-dashboard-data";
import { DashboardData } from "features/dashboard/types";

export function DashboardPage() {
  return (
    <DashboardErrorBoundary>
      <DashboardContent />
    </DashboardErrorBoundary>
  );
}

function DashboardContent() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboard = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const nextData = await getDashboardData();
      setData(nextData);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Unable to load observability workspace.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void loadDashboard();
  }, []);

  if (isLoading) {
    return <DashboardLoadingState />;
  }

  if (!data || error) {
    return (
      <DashboardShell
        heading="Observability workspace"
        subheading="PulseOps centralizes service health, incident posture, and uptime telemetry for internal operators."
        actions={<Badge className="bg-rose-500/10 text-rose-200">Action required</Badge>}
      >
        <div className="panel-surface panel-glow rounded-3xl px-6 py-10 text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-rose-500/10 text-rose-300">
            <BellRing className="h-7 w-7" />
          </div>
          <h2 className="mt-5 text-2xl font-semibold text-white">Unable to reach dashboard data</h2>
          <p className="mx-auto mt-3 max-w-xl text-sm text-slate-400">{error ?? "Retry when the PulseOps API is available."}</p>
          <Button className="mt-6" onClick={() => void loadDashboard()}>
            Retry data sync
          </Button>
        </div>
      </DashboardShell>
    );
  }

  return (
    <DashboardShell
      heading={`${data.summary.teamName} workspace`}
      subheading="Modern internal observability dashboard for SRE teams, with focused service posture, incident routing, and regional uptime views."
      actions={
        <>
          <Badge>Dark mode default</Badge>
          <Badge className="bg-emerald-500/10 text-emerald-200">{data.summary.monthlyAvailability} availability</Badge>
        </>
      }
    >
      <ServiceOverviewGrid data={data} />

      <div className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1.35fr)_minmax(0,0.9fr)]">
        <div className="min-w-0 space-y-5">
          <MetricsCharts charts={data.metricsCharts} />
          <ErrorMonitoringTable events={data.errorEvents} />
        </div>
        <div className="min-w-0 space-y-5">
          <ServiceStatusPanel services={data.services} />
          <UptimeVisualization regions={data.uptimeRegions} />
          <AutomationEmptyState automations={data.automations} />
        </div>
      </div>
    </DashboardShell>
  );
}
