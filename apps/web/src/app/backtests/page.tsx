import { ActionButton } from "@/components/ActionButton";
import { SectionTitle } from "@/components/ui";

export default function BacktestsPage() {
  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <p className="text-[11px] uppercase tracking-[0.2em] text-accent">Simulation</p>
        <h1 className="mt-2 font-display text-3xl text-ink">Backtests</h1>
        <p className="mt-2 text-sm text-ink-muted">
          Bar engine with fees, slippage, and validation gates. Accept or reject with evidence.
        </p>
      </div>

      <section className="panel p-5">
        <SectionTitle title="Momentum (SMA)" subtitle="Hypothesis: intermediate trends persist" />
        <ActionButton
          label="Run momentum backtest"
          path="/api/v1/backtests/run"
          demo
          body={{ symbol: "RELIANCE", family: "momentum", provider: "fixture", persist: true }}
        />
      </section>

      <section className="panel p-5">
        <SectionTitle title="Mean reversion" subtitle="Hypothesis: z-score dips reverse" />
        <ActionButton
          label="Run mean-reversion backtest"
          path="/api/v1/backtests/run"
          demo
          body={{ symbol: "TCS", family: "mean_reversion", provider: "fixture", persist: true }}
        />
      </section>
    </div>
  );
}
