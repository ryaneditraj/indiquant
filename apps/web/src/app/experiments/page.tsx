"use client";

import { useEffect, useState } from "react";

import { EquityChart } from "@/components/EquityChart";
import { SectionTitle } from "@/components/ui";
import { apiBase } from "@/lib/api";

type Experiment = {
  id: string;
  status: string;
  ai_summary: string;
  rejection_reason?: string;
  reproducibility_score?: number;
  outputs?: { equity_curve?: Array<{ ts?: string; equity: number }> };
  metrics?: Record<string, number>;
};

export default function ExperimentsPage() {
  const [experiments, setExperiments] = useState<Experiment[]>([]);

  useEffect(() => {
    fetch(`${apiBase()}/api/v1/experiments`)
      .then((r) => (r.ok ? r.json() : []))
      .then(setExperiments)
      .catch(() => setExperiments([]));
  }, []);

  const latestWithCurve = experiments.find((e) => (e.outputs?.equity_curve || []).length > 0);

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div>
        <p className="text-[11px] uppercase tracking-[0.2em] text-accent">Reproducible runs</p>
        <h1 className="mt-2 font-display text-3xl text-ink">Experiments</h1>
        <p className="mt-2 text-sm text-ink-muted">
          UUID, inputs, metrics, AI summary, rejection reasons, reproducibility score.
        </p>
      </div>

      {latestWithCurve ? (
        <section className="panel p-5">
          <SectionTitle
            title="Latest equity curve"
            subtitle={latestWithCurve.ai_summary || latestWithCurve.id}
          />
          <EquityChart data={latestWithCurve.outputs?.equity_curve || []} />
        </section>
      ) : null}

      <section className="panel overflow-hidden">
        <div className="border-b border-canvas-border px-5 py-3">
          <SectionTitle title={`${experiments.length} stored`} />
        </div>
        <div className="divide-y divide-canvas-border">
          {experiments.map((e) => (
            <div key={e.id} className="grid gap-2 px-5 py-4 md:grid-cols-[1fr_120px_100px]">
              <div>
                <p className="text-sm text-ink">{e.ai_summary || "No summary"}</p>
                <p className="mt-1 font-mono text-[10px] text-ink-faint">{e.id}</p>
                {e.rejection_reason ? (
                  <p className="mt-1 text-xs text-accent-bad">{e.rejection_reason}</p>
                ) : null}
                {e.metrics?.sharpe != null ? (
                  <p className="mt-1 font-mono text-[10px] text-ink-muted">
                    sharpe {Number(e.metrics.sharpe).toFixed(3)} · maxdd{" "}
                    {Number(e.metrics.max_drawdown || 0).toFixed(3)}
                  </p>
                ) : null}
              </div>
              <p className="font-mono text-xs text-ink-muted">
                repro {Number(e.reproducibility_score || 0).toFixed(2)}
              </p>
              <p
                className={`text-xs uppercase tracking-wide ${
                  e.status === "accepted" ? "text-accent-good" : "text-accent-warn"
                }`}
              >
                {e.status}
              </p>
            </div>
          ))}
          {!experiments.length && (
            <p className="px-5 py-8 text-sm text-ink-muted">Empty. Start from Research or Backtests.</p>
          )}
        </div>
      </section>
    </div>
  );
}
