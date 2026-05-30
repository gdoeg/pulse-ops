import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "components/ui/card";
import { UptimeRegion } from "features/dashboard/types";

export function UptimeVisualization({ regions }: { regions: UptimeRegion[] }) {
  return (
    <Card>
      <CardHeader>
        <CardDescription>Uptime placeholder</CardDescription>
        <CardTitle>Regional availability bands</CardTitle>
      </CardHeader>
      <CardContent className="space-y-5">
        {regions.map((region) => (
          <div key={region.region} className="rounded-2xl border border-white/5 bg-white/[0.02] p-4">
            <div className="flex items-end justify-between gap-3">
              <div>
                <h3 className="font-medium text-white">{region.region}</h3>
                <p className="mt-1 text-sm text-slate-400">{region.trend}</p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-semibold text-white">{region.availability.toFixed(2)}%</div>
                <div className="text-xs uppercase tracking-[0.2em] text-slate-500">30d availability</div>
              </div>
            </div>
            <div className="mt-4 flex items-end gap-2">
              {region.samples.map((sample, index) => (
                <div key={`${region.region}-${index}`} className="flex-1 rounded-full bg-white/5 p-1">
                  <div
                    className="rounded-full bg-gradient-to-t from-emerald-500/35 to-cyan-300/90"
                    style={{ height: `${Math.max(sample, 24)}%` }}
                  />
                </div>
              ))}
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
