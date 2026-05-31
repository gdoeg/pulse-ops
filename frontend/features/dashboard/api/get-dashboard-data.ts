import { DashboardData } from "features/dashboard/types";

export async function getDashboardData() {
  await new Promise((resolve) => setTimeout(resolve, 600));
  const response = await fetch("/api/dashboard", {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch dashboard data: ${response.status}`);
  }

  return response.json() as Promise<DashboardData>;
}
