import Link from "next/link";

import { SectionTitle } from "@/components/ui";

const GATES = [
  {
    name: "Walk-forward",
    detail: "Out-of-sample folds must stay positive on average",
  },
  {
    name: "Monte Carlo",
    detail: "Resampled equity tails must clear risk thresholds",
  },
  {
    name: "Lookahead / leakage",
    detail: "Signals must not track same-bar returns suspiciously",
  },
  {
    name: "Parameter sensitivity",
    detail: "Sharpe surface must not be explosively unstable",
  },
  {
    name: "Reproducibility score",
    detail: "Seed, symbol window, and metrics must be present",
  },
];

export default function ValidationPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <p className="text-[11px] uppercase tracking-[0.2em] text-accent">Scientific gates</p>
        <h1 className="mt-2 font-display text-3xl text-ink">Validation</h1>
        <p className="mt-2 text-sm text-ink-muted">
          Every backtest and research cycle runs these gates automatically. Fail any configured
          check → reject. Thresholds live in{" "}
          <code className="font-mono text-accent">config.yaml → validation</code>.
        </p>
      </div>

      <section className="panel p-5">
        <SectionTitle
          title="Gate suite"
          subtitle="Executed inside validate_strategy — not a separate UI workflow"
        />
        <ul className="space-y-3">
          {GATES.map((g) => (
            <li key={g.name} className="border-b border-canvas-border/70 pb-3 last:border-0 last:pb-0">
              <p className="text-sm text-ink">{g.name}</p>
              <p className="mt-0.5 text-xs text-ink-muted">{g.detail}</p>
            </li>
          ))}
        </ul>
      </section>

      <section className="panel p-5">
        <SectionTitle title="Run a validated experiment" />
        <p className="mb-3 text-sm text-ink-muted">
          Validation results appear on the experiment after a cycle or backtest.
        </p>
        <div className="flex flex-wrap gap-3 text-sm">
          <Link href="/backtests" className="text-accent hover:underline">
            Backtests →
          </Link>
          <Link href="/research" className="text-accent hover:underline">
            Research →
          </Link>
          <Link href="/experiments" className="text-accent hover:underline">
            Experiments →
          </Link>
        </div>
      </section>
    </div>
  );
}
