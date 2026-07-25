"use client";

import { useCallback, useEffect, useState } from "react";

import { ActionButton } from "@/components/ActionButton";
import { Button } from "@/components/Button";
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
  const [chatError, setChatError] = useState("");
  const [chatBusy, setChatBusy] = useState(false);
  const [loop, setLoop] = useState<LoopState | null>(null);
  const [loopError, setLoopError] = useState("");

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
    setChatBusy(true);
    setChatError("");
    setReply("");
    try {
      const res = await fetch(`${apiBase()}/api/v1/ai/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [{ role: "user", content: input }],
          experiment_ids: loop?.last_experiment_id ? [loop.last_experiment_id] : [],
        }),
      });
      const json = await res.json();
      if (!res.ok) {
        setChatError(typeof json.detail === "string" ? json.detail : `error ${res.status}`);
        return;
      }
      setReply(json.content || JSON.stringify(json));
    } catch (err) {
      setChatError(String(err));
    } finally {
      setChatBusy(false);
    }
  }

  async function loopAction(path: string, body?: Record<string, unknown>) {
    setLoopError("");
    try {
      const res = await fetch(`${apiBase()}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: body ? JSON.stringify(body) : undefined,
      });
      if (!res.ok) {
        const json = await res.json().catch(() => ({}));
        setLoopError(typeof json.detail === "string" ? json.detail : `error ${res.status}`);
      }
      refreshLoop();
    } catch (err) {
      setLoopError(String(err));
    }
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

      <section className="panel space-y-4 p-5">
        <SectionTitle
          title="Forever loop"
          subtitle={`Status: ${loop?.status ?? "…"} · cycles ${loop?.cycles_completed ?? 0} · accepted ${loop?.accepted ?? 0} · rejected ${loop?.rejected ?? 0}`}
        />
        <div className="flex flex-wrap gap-2">
          <Button
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
          </Button>
          <Button variant="secondary" onClick={() => loopAction("/api/v1/ai/loop/pause")}>
            Pause
          </Button>
          <Button variant="secondary" onClick={() => loopAction("/api/v1/ai/loop/resume")}>
            Resume
          </Button>
          <Button variant="danger" onClick={() => loopAction("/api/v1/ai/loop/stop")}>
            Stop
          </Button>
        </div>
        {loopError ? <p className="text-xs text-accent-bad">{loopError}</p> : null}
        {loop?.last_error ? <p className="text-xs text-accent-bad">{loop.last_error}</p> : null}
        <ul className="space-y-2 text-xs text-ink-muted">
          {(loop?.history || []).slice(-5).map((h, i) => (
            <li key={i}>
              {String(h.symbol)} · {h.accepted ? "accepted" : "rejected"} ·{" "}
              <span className="font-mono text-ink-faint">{String(h.experiment_id)}</span>
            </li>
          ))}
          {!loop?.history?.length ? (
            <li className="text-ink-faint">No cycles yet — hit Start to begin scanning.</li>
          ) : null}
        </ul>
      </section>

      <section className="panel p-5">
        <SectionTitle title="Single cycle" />
        <ActionButton
          label="Run CEO research cycle"
          path="/api/v1/ai/cycle"
          demo
          body={{ symbol: "INFY", lookback_days: 250, seed: 7, provider: "fixture", persist: true }}
        />
      </section>

      <section className="panel space-y-3 p-5">
        <SectionTitle title="Research chat" subtitle="Cites last loop experiment when available" />
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="min-h-24 w-full rounded-xl border border-canvas-border bg-canvas p-3 text-sm text-ink outline-none ring-accent focus:ring-1"
        />
        <Button disabled={chatBusy || !input.trim()} onClick={chat}>
          {chatBusy ? "Thinking…" : "Ask"}
        </Button>
        {chatError ? <p className="text-sm text-accent-bad">{chatError}</p> : null}
        {reply ? (
          <pre className="whitespace-pre-wrap rounded-xl bg-canvas p-3 text-xs text-ink-muted">{reply}</pre>
        ) : null}
      </section>
    </div>
  );
}
