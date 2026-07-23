"use client";

import { useCallback, useEffect, useState } from "react";

import { ActionButton } from "@/components/ActionButton";
import { SectionTitle } from "@/components/ui";
import { apiBase } from "@/lib/api";

type LoopState = {
  status: string;
  cycles_completed: number;
  accepted: number;
  rejected: number;
  last_experiment_id: string;
  last_error: string;
  history: Array<Record<string, unknown>>;
};

export default function AILabPage() {
  const [input, setInput] = useState("Why might a momentum strategy fail in sideways regimes?");
  const [reply, setReply] = useState("");
  const [loop, setLoop] = useState<LoopState | null>(null);

  const refreshLoop = useCallback(() => {
    fetch(`${apiBase()}/api/v1/ai/loop`)
      .then((r) => (r.ok ? r.json() : null))
      .then(setLoop)
      .catch(() => setLoop(null));
  }, []);

  useEffect(() => {
    refreshLoop();
    const id = setInterval(refreshLoop, 2000);
    return () => clearInterval(id);
  }, [refreshLoop]);

  async function chat() {
    const res = await fetch(`${apiBase()}/api/v1/ai/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: [{ role: "user", content: input }],
        experiment_ids: loop?.last_experiment_id ? [loop.last_experiment_id] : [],
      }),
    });
    const json = await res.json();
    setReply(json.content || JSON.stringify(json));
  }

  async function loopAction(path: string, body?: Record<string, unknown>) {
    await fetch(`${apiBase()}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: body ? JSON.stringify(body) : undefined,
    });
    refreshLoop();
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <p className="text-[11px] uppercase tracking-[0.2em] text-accent">Agent laboratory</p>
        <h1 className="mt-2 font-display text-3xl text-ink">AI Lab</h1>
        <p className="mt-2 text-sm text-ink-muted">
          Forever research loop with pause/resume, single cycles, and evidence-bound chat.
        </p>
      </div>

      <section className="panel p-5 space-y-4">
        <SectionTitle
          title="Forever loop"
          subtitle={`Status: ${loop?.status ?? "…"} · cycles ${loop?.cycles_completed ?? 0} · accepted ${loop?.accepted ?? 0} · rejected ${loop?.rejected ?? 0}`}
        />
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            className="rounded-md bg-accent px-3 py-1.5 text-sm text-canvas"
            onClick={() =>
              loopAction("/api/v1/ai/loop/start", {
                symbols: ["RELIANCE", "TCS", "INFY"],
                provider: "fixture",
                interval_seconds: 1.5,
                max_cycles: 3,
              })
            }
          >
            Start (3 cycles)
          </button>
          <button
            type="button"
            className="rounded-md border border-canvas-border px-3 py-1.5 text-sm text-ink"
            onClick={() => loopAction("/api/v1/ai/loop/pause")}
          >
            Pause
          </button>
          <button
            type="button"
            className="rounded-md border border-canvas-border px-3 py-1.5 text-sm text-ink"
            onClick={() => loopAction("/api/v1/ai/loop/resume")}
          >
            Resume
          </button>
          <button
            type="button"
            className="rounded-md border border-accent-bad/40 px-3 py-1.5 text-sm text-accent-bad"
            onClick={() => loopAction("/api/v1/ai/loop/stop")}
          >
            Stop
          </button>
        </div>
        {loop?.last_error ? (
          <p className="text-xs text-accent-bad">{loop.last_error}</p>
        ) : null}
        <ul className="space-y-2 text-xs text-ink-muted">
          {(loop?.history || []).slice(-5).map((h, i) => (
            <li key={i}>
              {String(h.symbol)} · {h.accepted ? "accepted" : "rejected"} ·{" "}
              <span className="font-mono text-ink-faint">{String(h.experiment_id)}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="panel p-5">
        <SectionTitle title="Single cycle" />
        <ActionButton
          label="Run CEO research cycle"
          path="/api/v1/ai/cycle"
          body={{ symbol: "INFY", lookback_days: 250, seed: 7, provider: "fixture", persist: true }}
        />
      </section>

      <section className="panel p-5 space-y-3">
        <SectionTitle title="Research chat" subtitle="Cites last loop experiment when available" />
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="min-h-24 w-full rounded-md border border-canvas-border bg-canvas p-3 text-sm text-ink outline-none ring-accent focus:ring-1"
        />
        <button
          type="button"
          onClick={chat}
          className="rounded-md bg-accent px-3 py-1.5 text-sm font-medium text-canvas"
        >
          Ask
        </button>
        {reply ? (
          <pre className="whitespace-pre-wrap rounded-lg bg-canvas p-3 text-xs text-ink-muted">{reply}</pre>
        ) : null}
      </section>
    </div>
  );
}
