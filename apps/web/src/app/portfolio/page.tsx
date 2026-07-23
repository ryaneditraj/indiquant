import { ActionButton } from "@/components/ActionButton";
import { SectionTitle } from "@/components/ui";

export default function PortfolioPage() {
  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <p className="text-[11px] uppercase tracking-[0.2em] text-accent">Portfolio lab</p>
        <h1 className="mt-2 font-display text-3xl text-ink">Portfolio</h1>
        <p className="mt-2 text-sm text-ink-muted">
          Correlation, equal-weight risk contribution, and a sampled efficient frontier across
          strategy equity curves.
        </p>
      </div>
      <section className="panel p-5">
        <SectionTitle title="Analyze basket" subtitle="RELIANCE · TCS · INFY" />
        <ActionButton
          label="Run portfolio analysis"
          path="/api/v1/portfolio/analyze"
          body={{ symbols: ["RELIANCE", "TCS", "INFY"] }}
        />
      </section>
    </div>
  );
}
