import Link from "next/link";

import { SectionTitle } from "@/components/ui";
import { fetchExperiments } from "@/lib/api";

export default async function ExperimentsPage() {
  const experiments = (await fetchExperiments()) || [];

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div>
        <p className="text-[11px] uppercase tracking-[0.2em] text-accent">Reproducible runs</p>
        <h1 className="mt-2 font-display text-3xl text-ink">Experiments</h1>
        <p className="mt-2 text-sm text-ink-muted">
          UUID, inputs, metrics, AI summary, rejection reasons, reproducibility score.
        </p>
      </div>

      <section className="panel overflow-hidden">
        <div className="border-b border-canvas-border px-5 py-3">
          <SectionTitle title={`${experiments.length} stored`} />
        </div>
        <div className="divide-y divide-canvas-border">
          {experiments.map((e) => (
            <div key={String(e.id)} className="grid gap-2 px-5 py-4 md:grid-cols-[1fr_120px_100px]">
              <div>
                <p className="text-sm text-ink">{String(e.ai_summary || "No summary")}</p>
                <p className="mt-1 font-mono text-[10px] text-ink-faint">{String(e.id)}</p>
                {e.rejection_reason ? (
                  <p className="mt-1 text-xs text-accent-bad">{String(e.rejection_reason)}</p>
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
                {String(e.status)}
              </p>
            </div>
          ))}
          {!experiments.length && (
            <p className="px-5 py-8 text-sm text-ink-muted">
              Empty. Start from <Link href="/research">Research</Link> or Backtests.
            </p>
          )}
        </div>
      </section>
    </div>
  );
}
