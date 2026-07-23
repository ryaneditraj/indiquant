import { ActionButton } from "@/components/ActionButton";
import { SectionTitle } from "@/components/ui";
import { fetchHypotheses } from "@/lib/api";

export default async function ResearchPage() {
  const hypotheses = (await fetchHypotheses()) || [];

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div>
        <p className="text-[11px] uppercase tracking-[0.2em] text-accent">Hypothesis first</p>
        <h1 className="mt-2 font-display text-3xl text-ink">Research</h1>
        <p className="mt-2 text-sm text-ink-muted">
          Invent theses before code. Never random indicator soup. Run a full AI research cycle to
          generate → backtest → validate → accept/reject.
        </p>
      </div>

      <section className="panel p-5">
        <SectionTitle title="Run research cycle" subtitle="CEO orchestrates Data → Research → Quant → Critic → Risk" />
        <ActionButton
          label="Discover on RELIANCE"
          path="/api/v1/ai/cycle"
          body={{ symbol: "RELIANCE", lookback_days: 365, seed: 42, provider: "fixture", persist: true }}
        />
      </section>

      <section className="panel p-5">
        <SectionTitle title="Hypotheses" />
        <ul className="space-y-3">
          {hypotheses.map((h) => (
            <li key={String(h.id)} className="border-b border-canvas-border pb-3 last:border-0">
              <p className="text-sm text-ink">{String(h.title)}</p>
              <p className="mt-1 text-xs text-ink-muted">{String(h.thesis)}</p>
              <p className="mt-1 font-mono text-[10px] text-ink-faint">
                {String(h.family)} · {String(h.id)}
              </p>
            </li>
          ))}
          {!hypotheses.length && (
            <li className="text-sm text-ink-muted">No hypotheses yet — run a research cycle.</li>
          )}
        </ul>
      </section>
    </div>
  );
}
