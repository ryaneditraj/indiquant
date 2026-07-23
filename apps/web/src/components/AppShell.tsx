"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";

import { apiBase } from "@/lib/api";

const FALLBACK_NAV = [
  { id: "dashboard", label: "Dashboard", href: "/" },
  { id: "research", label: "Research", href: "/research" },
  { id: "experiments", label: "Experiments", href: "/experiments" },
  { id: "strategies", label: "Strategies", href: "/strategies" },
  { id: "datasets", label: "Datasets", href: "/datasets" },
  { id: "backtests", label: "Backtests", href: "/backtests" },
  { id: "validation", label: "Validation", href: "/validation" },
  { id: "optimization", label: "Optimization", href: "/optimization" },
  { id: "portfolio", label: "Portfolio", href: "/portfolio" },
  { id: "ai-lab", label: "AI Lab", href: "/ai-lab" },
  { id: "notebook", label: "Notebook", href: "/notebook" },
  { id: "logs", label: "Logs", href: "/logs" },
  { id: "settings", label: "Settings", href: "/settings" },
  { id: "docs", label: "Documentation", href: "/docs" },
];

const appName = process.env.NEXT_PUBLIC_APP_NAME || "Research OS";

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [query, setQuery] = useState("");
  const [hits, setHits] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    if (query.trim().length < 2) {
      setHits(null);
      return;
    }
    const handle = setTimeout(() => {
      fetch(`${apiBase()}/api/v1/search?q=${encodeURIComponent(query)}`)
        .then((r) => (r.ok ? r.json() : null))
        .then(setHits)
        .catch(() => setHits(null));
    }, 250);
    return () => clearTimeout(handle);
  }, [query]);

  return (
    <div className="flex min-h-screen">
      <aside className="sticky top-0 flex h-screen w-56 shrink-0 flex-col border-r border-canvas-border bg-canvas/90 px-3 py-5 backdrop-blur-md">
        <div className="mb-8 px-2">
          <p className="font-display text-2xl tracking-tight text-ink">{appName}</p>
          <p className="mt-1 text-[11px] uppercase tracking-[0.18em] text-ink-faint">
            Quant research OS
          </p>
        </div>
        <nav className="flex flex-1 flex-col gap-0.5 overflow-y-auto">
          {FALLBACK_NAV.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.id}
                href={item.href}
                className={`relative rounded-md px-2.5 py-1.5 text-sm transition-colors ${
                  active ? "text-ink" : "text-ink-muted hover:text-ink"
                }`}
              >
                {active && (
                  <motion.span
                    layoutId="nav-active"
                    className="absolute inset-0 rounded-md bg-accent-soft/60"
                    transition={{ type: "spring", stiffness: 380, damping: 32 }}
                  />
                )}
                <span className="relative z-10">{item.label}</span>
              </Link>
            );
          })}
        </nav>
        <p className="px-2 pt-4 font-mono text-[10px] text-ink-faint">Phase 1–6 · evidence first</p>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-20 flex h-12 items-center justify-between gap-4 border-b border-canvas-border bg-canvas/70 px-6 backdrop-blur-md">
          <div className="relative min-w-0 flex-1 max-w-md">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search strategies, experiments, hypotheses…"
              className="w-full rounded-md border border-canvas-border bg-canvas px-3 py-1.5 text-sm text-ink outline-none ring-accent focus:ring-1"
            />
            {hits && (
              <div className="absolute left-0 right-0 top-9 z-30 panel max-h-72 overflow-auto p-3 text-xs">
                {(["strategies", "experiments", "hypotheses"] as const).map((key) => (
                  <div key={key} className="mb-2">
                    <p className="mb-1 uppercase tracking-wider text-ink-faint">{key}</p>
                    {((hits[key] as Array<Record<string, unknown>>) || []).map((item) => (
                      <p key={String(item.id)} className="truncate text-ink-muted">
                        {String(item.name || item.title || item.summary || item.id)}
                      </p>
                    ))}
                  </div>
                ))}
              </div>
            )}
          </div>
          <div className="flex items-center gap-3 font-mono text-[11px] text-ink-faint">
            <span className="inline-flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-accent-good" />
              local
            </span>
            <span>IN · NSE/BSE</span>
          </div>
        </header>
        <main className="flex-1 bg-grid bg-[length:48px_48px] p-6">{children}</main>
      </div>
    </div>
  );
}
