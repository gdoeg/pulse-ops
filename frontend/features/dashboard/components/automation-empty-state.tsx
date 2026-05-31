import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "components/ui/card";

export function AutomationEmptyState({ automations }: { automations: string[] }) {
  return (
    <Card>
      <CardHeader>
        <CardDescription>Empty state</CardDescription>
        <CardTitle>Incident automations</CardTitle>
      </CardHeader>
      <CardContent>
        {automations.length > 0 ? (
          <ul className="space-y-3 text-sm text-slate-300">
            {automations.map((automation) => (
              <li key={automation} className="rounded-xl border border-white/5 bg-white/[0.02] px-3 py-2.5">
                {automation}
              </li>
            ))}
          </ul>
        ) : (
          <div className="rounded-xl border border-dashed border-white/10 bg-white/[0.02] px-5 py-8">
            <p className="text-base font-medium text-white">No automation policies configured</p>
            <p className="mt-2 text-sm text-slate-400">
              Create routing or remediation workflows to surface runbooks, paging rules, and rollback tasks here.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
