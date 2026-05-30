import { mockDashboardData } from "features/dashboard/data/mock-dashboard";

export async function GET() {
  return Response.json(mockDashboardData);
}
