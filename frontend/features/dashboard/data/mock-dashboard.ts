import { DashboardData } from "features/dashboard/types";

export const mockDashboardData: DashboardData = {
  summary: {
    teamName: "Platform Reliability",
    monitoredServices: 18,
    openAlerts: 3,
    monthlyAvailability: "99.982%",
    lastUpdated: "2 min ago",
  },
  services: [
    { name: "edge-gateway", tier: "Tier 0", status: "healthy", latencyMs: 74, errorRate: "0.06%", throughput: "42k rpm" },
    { name: "workflow-engine", tier: "Tier 1", status: "degraded", latencyMs: 182, errorRate: "0.48%", throughput: "18k rpm" },
    { name: "incident-api", tier: "Tier 1", status: "healthy", latencyMs: 92, errorRate: "0.09%", throughput: "26k rpm" },
    { name: "telemetry-fanout", tier: "Tier 0", status: "critical", latencyMs: 248, errorRate: "1.14%", throughput: "12k rpm" },
  ],
  metricsCharts: [
    { id: "request-volume", title: "Request volume", change: "+8.4% vs last hour", points: [28, 34, 29, 41, 47, 45, 58, 62, 59, 68, 74, 72] },
    { id: "p95-latency", title: "P95 latency", change: "-14ms stabilized", points: [72, 68, 74, 78, 84, 71, 67, 63, 58, 54, 56, 52] },
    { id: "error-budget", title: "Error budget burn", change: "0.78x burn rate", points: [46, 40, 42, 39, 33, 35, 31, 27, 29, 24, 22, 18] },
  ],
  errorEvents: [
    {
      service: "telemetry-fanout",
      issue: "Kafka consumer lag exceeded SLO threshold",
      severity: "critical",
      impactedRegion: "us-east-1",
      detectedAt: "7 min ago",
    },
    {
      service: "workflow-engine",
      issue: "Elevated queue retries on async orchestration path",
      severity: "high",
      impactedRegion: "eu-west-1",
      detectedAt: "14 min ago",
    },
    {
      service: "incident-api",
      issue: "Intermittent 502 spikes behind API gateway",
      severity: "medium",
      impactedRegion: "global",
      detectedAt: "39 min ago",
    },
  ],
  uptimeRegions: [
    { region: "us-east-1", availability: 99.99, trend: "Stable", samples: [96, 98, 97, 99, 99, 100, 99, 98, 100, 99] },
    { region: "eu-west-1", availability: 99.97, trend: "Recovering", samples: [92, 94, 95, 94, 96, 97, 98, 99, 99, 100] },
    { region: "ap-southeast-1", availability: 99.95, trend: "Watching", samples: [89, 90, 91, 92, 93, 95, 96, 96, 97, 98] },
  ],
  automations: [],
};
