import { notFound } from "next/navigation";

import { SectionTitle } from "@/components/ui";
import { apiBase } from "@/lib/api";

async function getStrategy(id: string) {
  try {
    const res = await fetch(`${apiBase()}/api/v1/strategies/${id}`, { next: { revalidate: 5 } });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export default async function StrategyDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const strategy = await getStrategy(id);
  if (!strategy) notFound();

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <p className="text-[11px] uppercase tracking-[0.2em] text-accent">Strategy</p>
        <h1 className="mt-2 font-display text-3xl text-ink">{String(strategy.name)}</h1>
        <p className="mt-2 font-mono text-[11px] text-ink-faint">{String(strategy.id)}</p>
      </div>

      <section className="panel p-5">
        <SectionTitle title="Idea" />
        <p className="text-sm text-ink-muted">{String(strategy.idea)}</p>
      </section>
      <section className="panel p-5">
        <SectionTitle title="Logic" />
        <p className="text-sm text-ink-muted">{String(strategy.logic_summary)}</p>
      </section>
      <section className="panel p-5">
        <SectionTitle title="Code" />
        <pre className="overflow-auto rounded-lg bg-canvas p-3 font-mono text-xs text-accent">
          {String(strategy.code)}
        </pre>
      </section>
      <section className="panel p-5">
        <SectionTitle title="Parameters / regimes" />
        <pre className="font-mono text-xs text-ink-muted">
          {JSON.stringify({ parameters: strategy.parameters, regimes: strategy.regimes }, null, 2)}
        </pre>
      </section>
      <section className="panel p-5">
        <SectionTitle title="Weaknesses / AI notes" />
        <p className="text-sm text-accent-bad">{String(strategy.weaknesses || "—")}</p>
        <p className="mt-2 text-sm text-ink-muted">{String(strategy.ai_notes || "—")}</p>
      </section>
    </div>
  );
}
