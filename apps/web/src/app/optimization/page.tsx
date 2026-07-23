import { SectionTitle } from "@/components/ui";

export default function OptimizationPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <p className="text-[11px] uppercase tracking-[0.2em] text-accent">Robustness</p>
        <h1 className="mt-2 font-display text-3xl text-ink">Optimization</h1>
        <p className="mt-2 text-sm text-ink-muted">
          Parameter sensitivity is part of validation. Prefer stable surfaces over peak Sharpe
          hunting.
        </p>
      </div>
      <section className="panel p-5">
        <SectionTitle
          title="Sensitivity grid"
          subtitle="Executed automatically inside validate_strategy / backtests"
        />
        <p className="text-sm text-ink-muted">
          See rejection reason <code className="font-mono text-accent">parameter surface</code> when
          instability is detected.
        </p>
      </section>
    </div>
  );
}
