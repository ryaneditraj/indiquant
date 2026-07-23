import { ActionButton } from "@/components/ActionButton";
import { SectionTitle } from "@/components/ui";
import { fetchDatasets, fetchProviders } from "@/lib/api";

export default async function DatasetsPage() {
  const [datasetsRes, providersRes] = await Promise.all([fetchDatasets(), fetchProviders()]);
  const datasets = datasetsRes?.datasets || [];
  const providers = providersRes?.providers || [];

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div>
        <p className="text-[11px] uppercase tracking-[0.2em] text-accent">Market data plane</p>
        <h1 className="mt-2 font-display text-3xl text-ink">Datasets</h1>
        <p className="mt-2 text-sm text-ink-muted">
          Modular NSE/BSE adapters. Parquet on disk. Configure DATA_* URLs — never hardcode.
        </p>
      </div>

      <section className="panel p-5">
        <SectionTitle title="Ingest (fixture / NSE)" />
        <ActionButton
          label="Ingest RELIANCE (fixture)"
          path="/api/v1/data/ingest"
          body={{
            symbol: "RELIANCE",
            start: "2023-01-01",
            end: "2024-12-31",
            provider: "fixture",
          }}
        />
      </section>

      <section className="panel p-5">
        <SectionTitle title="Providers" />
        <ul className="space-y-2">
          {providers.map((p) => (
            <li key={String(p.name)} className="flex justify-between gap-3 text-sm">
              <span className="text-ink">
                {String(p.name)}
                {p.default ? " · default" : ""}
              </span>
              <span className="font-mono text-xs text-ink-muted">
                {String((p.health as Record<string, unknown>)?.status || "—")}
              </span>
            </li>
          ))}
        </ul>
      </section>

      <section className="panel overflow-hidden">
        <div className="border-b border-canvas-border px-5 py-3">
          <SectionTitle title="Stored series" />
        </div>
        <div className="divide-y divide-canvas-border">
          {datasets.map((d) => (
            <div key={`${d.symbol}-${d.timeframe}`} className="grid gap-2 px-5 py-3 md:grid-cols-4">
              <p className="text-sm text-ink">{String(d.symbol)}</p>
              <p className="font-mono text-xs text-ink-muted">{String(d.timeframe)}</p>
              <p className="font-mono text-xs text-ink-muted">{String(d.rows)} rows</p>
              <p className="font-mono text-[10px] text-ink-faint">{String(d.freshness)}</p>
            </div>
          ))}
          {!datasets.length && (
            <p className="px-5 py-6 text-sm text-ink-muted">No parquet datasets yet.</p>
          )}
        </div>
      </section>
    </div>
  );
}
