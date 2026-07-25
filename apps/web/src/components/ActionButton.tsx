"use client";

import { useState } from "react";

import { Button } from "@/components/Button";
import { apiBase } from "@/lib/api";

function summarize(json: Record<string, unknown>): string {
  const lines: string[] = [];
  if (json.accepted != null) {
    lines.push(json.accepted ? "✓ accepted" : "✗ rejected");
  }
  if (json.persisted && typeof json.persisted === "object") {
    const p = json.persisted as Record<string, unknown>;
    if (p.experiment_id) lines.push(`experiment ${String(p.experiment_id).slice(0, 8)}…`);
  }
  if (json.experiment_id) lines.push(`experiment ${String(json.experiment_id).slice(0, 8)}…`);
  if (json.strategy_id) lines.push(`strategy ${String(json.strategy_id).slice(0, 8)}…`);
  const metrics = (json.metrics || (json.experiment as Record<string, unknown>)?.metrics) as
    | Record<string, number>
    | undefined;
  if (metrics?.sharpe != null) lines.push(`sharpe ${Number(metrics.sharpe).toFixed(3)}`);
  if (metrics?.max_drawdown != null) lines.push(`maxdd ${Number(metrics.max_drawdown).toFixed(3)}`);
  if (Array.isArray(json.rejection_reasons) && json.rejection_reasons.length) {
    lines.push(`reasons: ${(json.rejection_reasons as string[]).join(", ")}`);
  }
  if (json.rows != null) lines.push(`${json.rows} rows ingested`);
  if (json.symbol) lines.push(String(json.symbol));
  if (json.correlation) lines.push("portfolio report ready");
  if (!lines.length) return "done — see details below";
  return lines.join(" · ");
}

export function ActionButton({
  label,
  path,
  body,
  method = "POST",
  demo,
}: {
  label: string;
  path: string;
  body?: Record<string, unknown>;
  method?: string;
  demo?: boolean;
}) {
  const [summary, setSummary] = useState("");
  const [detail, setDetail] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [showRaw, setShowRaw] = useState(false);

  async function run() {
    setBusy(true);
    setError("");
    setSummary("");
    setDetail("");
    try {
      const res = await fetch(`${apiBase()}${path}`, {
        method,
        headers: { "Content-Type": "application/json" },
        body: body ? JSON.stringify(body) : undefined,
      });
      const json = (await res.json()) as Record<string, unknown>;
      if (!res.ok) {
        setError(typeof json.detail === "string" ? json.detail : `error ${res.status}`);
        return;
      }
      setSummary(summarize(json));
      setDetail(JSON.stringify(json, null, 2));
    } catch (err) {
      setError(String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2">
        <Button disabled={busy} onClick={run}>
          {busy ? "Working…" : label}
        </Button>
        {demo ? (
          <span className="rounded-full border border-canvas-border px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider text-ink-faint">
            demo · fixture
          </span>
        ) : null}
      </div>
      {error ? <p className="text-sm text-accent-bad">{error}</p> : null}
      {summary ? (
        <div className="rounded-xl border border-canvas-border bg-canvas/60 p-3">
          <p className="text-sm text-ink">{summary}</p>
          {detail ? (
            <button
              type="button"
              className="mt-2 text-[11px] text-accent-radar hover:underline"
              onClick={() => setShowRaw((v) => !v)}
            >
              {showRaw ? "Hide raw" : "Show raw JSON"}
            </button>
          ) : null}
          {showRaw && detail ? (
            <pre className="mt-2 max-h-48 overflow-auto font-mono text-[10px] text-ink-muted">
              {detail.slice(0, 2000)}
            </pre>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
