"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/Button";
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
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [examples, setExamples] = useState<Array<Record<string, unknown>>>([]);

  useEffect(() => {
    fetch(`${apiBase()}/api/v1/notebook/examples`)
      .then((r) => (r.ok ? r.json() : null))
      .then((j) => setExamples(j?.notebooks || []))
      .catch(() => setExamples([]));
  }, []);

  async function run() {
    setBusy(true);
    setError("");
    setOutput("");
    try {
      const res = await fetch(`${apiBase()}/api/v1/notebook/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code }),
      });
      const json = await res.json();
      if (!res.ok) {
        setError(typeof json.detail === "string" ? json.detail : `error ${res.status}`);
        return;
      }
      setOutput(JSON.stringify(json, null, 2));
    } catch (err) {
      setError(String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <p className="text-[11px] uppercase tracking-[0.2em] text-accent">Notebooks</p>
        <h1 className="mt-2 font-display text-3xl text-ink">Notebook</h1>
        <p className="mt-2 text-sm text-ink-muted">
          Local research REPL for development. It is disabled when QUANT_OS_ENV is
          production or staging. Imports, file reads, and dunder escapes are blocked.
          This is not a multi-user sandbox.
        </p>
      </div>

      <section className="panel space-y-3 p-5">
        <SectionTitle title="Editor" />
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          className="min-h-48 w-full rounded-xl border border-canvas-border bg-canvas p-3 font-mono text-xs text-accent outline-none ring-accent focus:ring-1"
        />
        <Button disabled={busy || !code.trim()} onClick={run}>
          {busy ? "Running…" : "Run"}
        </Button>
        {error ? <p className="text-sm text-accent-bad">{error}</p> : null}
        {output ? (
          <pre className="max-h-72 overflow-auto rounded-xl bg-canvas p-3 font-mono text-[11px] text-ink-muted">
            {output}
          </pre>
        ) : null}
      </section>

      {examples.map((nb) => (
        <section key={String(nb.id)} className="panel space-y-2 p-5">
          <SectionTitle title={String(nb.title)} />
          <Button variant="ghost" className="!px-0" onClick={() => setCode(String(nb.code))}>
            Load into editor
          </Button>
        </section>
      ))}
    </div>
  );
}
