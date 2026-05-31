import { Badge } from "components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "components/ui/table";
import { ErrorEvent } from "features/dashboard/types";
import { cn } from "lib/utils";

const severityClasses = {
  critical: "bg-rose-500/10 text-rose-200",
  high: "bg-amber-500/10 text-amber-200",
  medium: "bg-sky-500/10 text-sky-200",
  low: "bg-slate-500/10 text-slate-200",
};

export function ErrorMonitoringTable({ events }: { events: ErrorEvent[] }) {
  return (
    <Card>
      <CardHeader>
        <CardDescription>Error monitoring</CardDescription>
        <CardTitle>Active exception and alert routing</CardTitle>
      </CardHeader>
      <CardContent>
        {events.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-white/10 bg-white/[0.02] px-6 py-10 text-center">
            <p className="text-base font-medium text-white">No active errors</p>
            <p className="mt-2 text-sm text-slate-400">PulseOps will populate this table when new incidents trigger routing rules.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <tr>
                  <TableHead>Service</TableHead>
                  <TableHead>Issue</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead>Region</TableHead>
                  <TableHead>Detected</TableHead>
                </tr>
              </TableHeader>
              <TableBody>
                {events.map((event) => (
                  <TableRow key={`${event.service}-${event.issue}`}>
                    <TableCell className="font-medium text-white">{event.service}</TableCell>
                    <TableCell className="min-w-52 max-w-sm break-words">{event.issue}</TableCell>
                    <TableCell>
                      <Badge className={cn("border-transparent capitalize", severityClasses[event.severity])}>{event.severity}</Badge>
                    </TableCell>
                    <TableCell>{event.impactedRegion}</TableCell>
                    <TableCell>{event.detectedAt}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
