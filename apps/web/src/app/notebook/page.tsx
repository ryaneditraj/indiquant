"use client";

import { useEffect, useState } from "react";

import { SectionTitle } from "@/components/ui";
import { apiBase } from "@/lib/api";

const DEFAULT_CODE = `provider = FixtureDataProvider()
rows = provider.get_ohlcv('RELIANCE', date(2024,1,1), date(2024,6,1))
bars = pd.DataFrame(rows)
signals = backtest.sma_crossover_signals(bars['close'])
out = backtest.run_bar_backtest(bars, signals)
result = out.metrics
print(result)
`;

export default function NotebookPage() {
  const [code, setCode] = useState(DEFAULT_CODE);
  const [output, setOutput] = useState("");
  const [examples, setExamples] = useState<Array<Record<string, unknown>>>([]);

  useEffect(() => {
    fetch(`${apiBase()}/api/v1/notebook/examples`)
      .then((r) => (r.ok ? r.json() : null))
      .then((j) => setExamples(j?.notebooks || []))
      .catch(() => setExamples([]));
  }, []);

  async function run() {
    const res = await fetch(`${apiBase()}/api/v1/notebook/execute`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code }),
    });
    const json = await res.json();
    setOutput(JSON.stringify(json, null, 2));
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <p className="text-[11px] uppercase tracking-[0.2em] text-accent">Notebooks</p>
        <h1 className="mt-2 font-display text-3xl text-ink">Notebook</h1>
        <p className="mt-2 text-sm text-ink-muted">
          Restricted server-side research REPL. Dangerous I/O is blocked.
        </p>
      </div>

      <section className="panel p-5 space-y-3">
        <SectionTitle title="Editor" />
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          className="min-h-48 w-full rounded-lg border border-canvas-border bg-canvas p-3 font-mono text-xs text-accent outline-none ring-accent focus:ring-1"
        />
        <button
          type="button"
          onClick={run}
          className="rounded-md bg-accent px-3 py-1.5 text-sm font-medium text-canvas"
        >
          Run
        </button>
        {output ? (
          <pre className="max-h-72 overflow-auto rounded-lg bg-canvas p-3 font-mono text-[11px] text-ink-muted">
            {output}
          </pre>
        ) : null}
      </section>

      {examples.map((nb) => (
        <section key={String(nb.id)} className="panel p-5 space-y-2">
          <SectionTitle title={String(nb.title)} />
          <button
            type="button"
            className="text-xs text-accent"
            onClick={() => setCode(String(nb.code))}
          >
            Load into editor
          </button>
        </section>
      ))}
    </div>
  );
}
