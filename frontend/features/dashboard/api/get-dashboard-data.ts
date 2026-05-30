import { apiClient } from "lib/api/client";

import { DashboardData } from "features/dashboard/types";

export async function getDashboardData() {
  await new Promise((resolve) => setTimeout(resolve, 600));
  return apiClient.get<DashboardData>("/api/dashboard");
}
