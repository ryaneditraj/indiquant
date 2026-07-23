"use client";

import { useState } from "react";

import { ActionButton } from "@/components/ActionButton";
import { SectionTitle } from "@/components/ui";
import { apiBase } from "@/lib/api";

export default function AILabPage() {
  const [input, setInput] = useState("Why might a momentum strategy fail in sideways regimes?");
  const [reply, setReply] = useState("");

  async function chat() {
    const res = await fetch(`${apiBase()}/api/v1/ai/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: [{ role: "user", content: input }],
        experiment_ids: [],
      }),
    });
    const json = await res.json();
    setReply(json.content || JSON.stringify(json));
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <p className="text-[11px] uppercase tracking-[0.2em] text-accent">Agent laboratory</p>
        <h1 className="mt-2 font-display text-3xl text-ink">AI Lab</h1>
        <p className="mt-2 text-sm text-ink-muted">
          Multi-agent research cycle + project-aware chat. Offline mode never invents metrics.
        </p>
      </div>

      <section className="panel p-5">
        <SectionTitle title="Forever-loop cycle (single iteration)" />
        <ActionButton
          label="Run CEO research cycle"
          path="/api/v1/ai/cycle"
          body={{ symbol: "INFY", lookback_days: 250, seed: 7, provider: "fixture", persist: true }}
        />
      </section>

      <section className="panel p-5 space-y-3">
        <SectionTitle title="Research chat" subtitle="Cites experiment IDs when provided" />
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
