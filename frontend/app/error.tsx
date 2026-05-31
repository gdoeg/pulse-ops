"use client";

import { AlertTriangle } from "lucide-react";

import { Button } from "components/ui/button";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-16">
      <div className="panel-surface panel-glow w-full max-w-lg rounded-3xl p-8 text-center">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-rose-500/10 text-rose-300">
          <AlertTriangle className="h-7 w-7" />
        </div>
        <h1 className="mt-6 text-2xl font-semibold text-white">Dashboard unavailable</h1>
        <p className="mt-3 text-sm text-slate-400">
          {error.message || "PulseOps could not load the observability workspace."}
        </p>
        <Button className="mt-6" onClick={reset}>
          Retry
        </Button>
      </div>
    </main>
  );
}
