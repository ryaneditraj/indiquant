"use client";

import { useState } from "react";

import { apiBase } from "@/lib/api";

export function ActionButton({
  label,
  path,
  body,
  method = "POST",
}: {
  label: string;
  path: string;
  body?: Record<string, unknown>;
  method?: string;
}) {
  const [status, setStatus] = useState<string>("");
  const [busy, setBusy] = useState(false);

  async function run() {
    setBusy(true);
    setStatus("running…");
    try {
      const res = await fetch(`${apiBase()}${path}`, {
        method,
        headers: { "Content-Type": "application/json" },
        body: body ? JSON.stringify(body) : undefined,
      });
      const json = await res.json();
      if (!res.ok) {
        setStatus(`error ${res.status}`);
        return;
      }
      setStatus(JSON.stringify(json, null, 2).slice(0, 1200));
    } catch (err) {
      setStatus(String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-3">
      <button
        type="button"
        disabled={busy}
        onClick={run}
        className="rounded-md bg-accent px-3 py-1.5 text-sm font-medium text-canvas disabled:opacity-50"
      >
        {busy ? "Working…" : label}
      </button>
      {status ? (
        <pre className="max-h-64 overflow-auto rounded-lg bg-canvas p-3 font-mono text-[11px] text-ink-muted">
          {status}
        </pre>
      ) : null}
    </div>
  );
}
