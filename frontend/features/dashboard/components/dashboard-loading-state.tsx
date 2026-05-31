import { DashboardShell } from "features/dashboard/components/dashboard-shell";

import { Badge } from "components/ui/badge";
import { Card, CardContent, CardHeader } from "components/ui/card";
import { Skeleton } from "components/ui/skeleton";

export function DashboardLoadingState() {
  return (
    <DashboardShell
      heading="Observability workspace"
      subheading="Loading live service health, incident summaries, and reliability telemetry."
      actions={<Badge>Syncing telemetry</Badge>}
    >
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <Card key={index}>
            <CardHeader>
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-8 w-20" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-3 w-32" />
            </CardContent>
          </Card>
        ))}
      </div>
      <div className="mt-6 grid gap-6 xl:grid-cols-[1.45fr,0.95fr]">
        <Card>
          <CardHeader>
            <Skeleton className="h-5 w-40" />
            <Skeleton className="h-3 w-64" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-56 w-full" />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <Skeleton className="h-5 w-28" />
            <Skeleton className="h-3 w-44" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-56 w-full" />
          </CardContent>
        </Card>
      </div>
    </DashboardShell>
  );
}
