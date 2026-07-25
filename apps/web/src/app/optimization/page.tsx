import Link from "next/link";

import { SectionTitle } from "@/components/ui";

export default function OptimizationPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <p className="text-[11px] uppercase tracking-[0.2em] text-accent">Robustness</p>
        <h1 className="mt-2 font-display text-3xl text-ink">Optimization</h1>
        <p className="mt-2 text-sm text-ink-muted">
          Indiquant prefers stable parameter surfaces over peak-Sharpe hunting. Sensitivity grids run
          inside validation — unstable strategies get rejected.
        </p>
      </div>

      <section className="panel p-5">
        <SectionTitle
          title="How it works today"
          subtitle="No separate optimizer UI yet — by design"
        />
        <p className="text-sm leading-relaxed text-ink-muted">
          When you run a backtest or AI research cycle, Indiquant sweeps nearby parameter
          combinations and checks whether performance collapses off the chosen point. That keeps
          “optimization” honest: evidence of robustness, not curve-fitting.
        </p>
      </section>

      <section className="panel p-5">
        <SectionTitle title="Try it" />
        <div className="flex flex-wrap gap-3 text-sm">
          <Link href="/backtests" className="text-accent hover:underline">
            Run a backtest →
          </Link>
          <Link href="/ai-lab" className="text-accent hover:underline">
            Start research loop →
          </Link>
        </div>
      </section>
    </div>
  );
}
