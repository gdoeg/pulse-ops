export type ServiceStatus = "healthy" | "degraded" | "critical";
export type AlertSeverity = "critical" | "high" | "medium" | "low";

export interface ServiceOverview {
  name: string;
  tier: string;
  status: ServiceStatus;
  latencyMs: number;
  errorRate: string;
  throughput: string;
}

export interface MetricChart {
  id: string;
  title: string;
  change: string;
  points: number[];
}

export interface ErrorEvent {
  service: string;
  issue: string;
  severity: AlertSeverity;
  impactedRegion: string;
  detectedAt: string;
}

export interface UptimeRegion {
  region: string;
  availability: number;
  trend: string;
  samples: number[];
}

export interface DashboardData {
  summary: {
    teamName: string;
    monitoredServices: number;
    openAlerts: number;
    monthlyAvailability: string;
    lastUpdated: string;
  };
  services: ServiceOverview[];
  metricsCharts: MetricChart[];
  errorEvents: ErrorEvent[];
  uptimeRegions: UptimeRegion[];
  automations: string[];
}
