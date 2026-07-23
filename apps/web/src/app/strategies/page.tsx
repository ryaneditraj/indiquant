import Link from "next/link";

import { SectionTitle } from "@/components/ui";
import { fetchStrategies } from "@/lib/api";

export default async function StrategiesPage() {
  const strategies = (await fetchStrategies()) || [];

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div>
        <p className="text-[11px] uppercase tracking-[0.2em] text-accent">Strategy archive</p>
        <h1 className="mt-2 font-display text-3xl text-ink">Strategies</h1>
        <p className="mt-2 text-sm text-ink-muted">
          Idea, logic, code, regimes, weaknesses — why it should work, and where it fails.
        </p>
      </div>

      <div className="grid gap-4">
        {strategies.map((s) => (
          <Link key={String(s.id)} href={`/strategies/${s.id}`} className="panel block p-5 transition hover:border-accent/40">
            <div className="flex items-start justify-between gap-3">
              <div>
                <h2 className="font-display text-xl text-ink">{String(s.name)}</h2>
                <p className="mt-1 text-sm text-ink-muted">{String(s.idea || s.logic_summary)}</p>
              </div>
              <span className="font-mono text-[10px] text-ink-faint">v{String(s.version)}</span>
            </div>
            <p className="mt-3 font-mono text-[11px] text-accent">{String(s.code)}</p>
            {s.weaknesses ? (
              <p className="mt-2 text-xs text-accent-bad">Weaknesses: {String(s.weaknesses)}</p>
            ) : null}
          </Link>
        ))}
        {!strategies.length && (
          <section className="panel p-5">
            <SectionTitle title="No strategies yet" subtitle="Run Research cycle or Backtests to materialize one." />
          </section>
        )}
      </div>
    </div>
  );
}
