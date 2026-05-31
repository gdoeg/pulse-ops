import { Activity, BellRing, ChartSpline, Command, HeartPulse, ShieldAlert } from "lucide-react";
import Link from "next/link";
import { ReactNode } from "react";

import { Badge } from "components/ui/badge";
import { Card } from "components/ui/card";
import { cn } from "lib/utils";

const navigation = [
  { label: "Overview", icon: Activity, active: true, href: "/" },
  { label: "Services", icon: Command, href: "/services" },
  { label: "Incidents", icon: ShieldAlert, href: "/incidents" },
  { label: "Uptime", icon: HeartPulse, href: "/uptime" },
  { label: "Analytics", icon: ChartSpline, href: "/analytics" },
];

export function DashboardShell({
  heading,
  subheading,
  children,
  actions,
}: {
  heading: string;
  subheading: string;
  children: ReactNode;
  actions?: ReactNode;
}) {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-[1600px] gap-5 px-3 py-4 sm:px-4 lg:px-5">
      <aside className="hidden w-64 shrink-0 lg:block">
        <Card className="sticky top-5 overflow-hidden">
          <div className="border-b border-white/10 px-5 py-5">
            <p className="text-xs uppercase tracking-[0.35em] text-cyan-300">PulseOps</p>
            <h1 className="mt-2 text-xl font-semibold text-white">Observability</h1>
            <p className="mt-2 text-sm text-slate-400">Operational command center for internal reliability teams.</p>
          </div>
          <nav className="space-y-1 p-3">
            {navigation.map(({ label, icon: Icon, active, href }) => (
              <Link
                key={label}
                href={href}
                className={cn(
                  "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-slate-400 transition-colors hover:bg-slate-400/10 hover:text-slate-300",
                  active && "bg-cyan-400/10 text-cyan-200 hover:bg-cyan-400/20",
                )}
              >
                <Icon className="h-4 w-4" />
                <span>{label}</span>
              </Link>
            ))}
          </nav>
          <div className="border-t border-white/10 px-5 py-4">
            <Badge className="bg-emerald-500/10 text-emerald-200">SRE on-call healthy</Badge>
          </div>
        </Card>
      </aside>

      <div className="min-w-0 flex-1">
        <header className="mb-5 flex flex-col gap-3 rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-4 sm:px-5 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div className="flex items-center gap-2 text-xs uppercase tracking-[0.28em] text-slate-500 lg:hidden">
              <BellRing className="h-4 w-4 text-cyan-300" />
              Internal engineering platform
            </div>
            <h2 className="mt-2 text-2xl font-semibold tracking-tight text-white sm:text-[1.75rem]">{heading}</h2>
            <p className="mt-2 max-w-3xl text-sm text-slate-400">{subheading}</p>
          </div>
          <div className="flex flex-wrap items-center gap-2.5">{actions}</div>
        </header>
        <div className="mb-5 flex gap-2 overflow-x-auto pb-1 lg:hidden">
          {navigation.map(({ label, active, href }) => (
            <Link
              key={label}
              href={href}
              className={cn(
                "whitespace-nowrap rounded-full border border-white/10 px-4 py-2 text-sm text-slate-400 transition-colors hover:border-slate-500/50 hover:bg-slate-400/5",
                active && "border-cyan-400/20 bg-cyan-400/10 text-cyan-200 hover:border-cyan-400/40 hover:bg-cyan-400/20",
              )}
            >
              {label}
            </Link>
          ))}
        </div>
        {children}
      </div>
    </main>
  );
}
