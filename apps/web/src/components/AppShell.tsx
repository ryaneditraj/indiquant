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
  { id: "docs", label: "Docs", href: "/docs" },
];

const appName = process.env.NEXT_PUBLIC_APP_NAME || "Pramana";

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
      <aside className="sticky top-0 flex h-screen w-[15.5rem] shrink-0 flex-col border-r border-canvas-border/80 bg-canvas/85 px-3 py-5 backdrop-blur-xl">
        <Link href="/" className="mb-7 flex items-center gap-3 px-2">
          <span className="brand-mark flex h-9 w-9 items-center justify-center rounded-xl shadow-[0_0_24px_rgba(200,245,74,0.25)]">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
              <path
                d="M4 17 L12 4 L20 17 Z"
                stroke="#06110d"
                strokeWidth="2.2"
                strokeLinejoin="round"
              />
              <circle cx="12" cy="14.5" r="2.2" fill="#06110d" />
            </svg>
          </span>
          <span>
            <span className="block font-display text-xl leading-none tracking-tight text-ink">
              {appName}
            </span>
            <span className="mt-1 block text-[10px] uppercase tracking-[0.22em] text-ink-faint">
              evidence first
            </span>
          </span>
        </Link>

        <nav className="flex flex-1 flex-col gap-0.5 overflow-y-auto pr-1">
          {FALLBACK_NAV.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.id}
                href={item.href}
                className={`relative rounded-lg px-2.5 py-1.5 text-[13px] transition-colors ${
                  active ? "text-ink" : "text-ink-muted hover:text-ink"
                }`}
              >
                {active && (
                  <motion.span
                    layoutId="nav-active"
                    className="absolute inset-0 rounded-lg bg-accent-soft/80 ring-1 ring-accent/20"
                    transition={{ type: "spring", stiffness: 380, damping: 32 }}
                  />
                )}
                <span className="relative z-10">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="mt-3 rounded-xl border border-canvas-border/70 bg-canvas-elevated/60 p-3">
          <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-ink-faint">Philosophy</p>
          <p className="mt-1.5 text-[11px] leading-relaxed text-ink-muted">
            Hypotheses before code. Reject without evidence. Keep every trail.
          </p>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-20 flex h-14 items-center justify-between gap-4 border-b border-canvas-border/80 bg-canvas/70 px-6 backdrop-blur-xl">
          <div className="relative min-w-0 flex-1 max-w-lg">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search experiments, strategies, hypotheses…"
              className="w-full rounded-xl border border-canvas-border bg-canvas-elevated/80 px-3.5 py-2 text-sm text-ink outline-none transition focus:border-accent/40 focus:ring-1 focus:ring-accent/30"
            />
            {hits && (
              <div className="absolute left-0 right-0 top-11 z-30 panel max-h-72 overflow-auto p-3 text-xs">
                {(["strategies", "experiments", "hypotheses"] as const).map((key) => (
                  <div key={key} className="mb-2 last:mb-0">
                    <p className="mb-1 uppercase tracking-wider text-ink-faint">{key}</p>
                    {((hits[key] as Array<Record<string, unknown>>) || []).map((item) => (
                      <p key={String(item.id)} className="truncate py-0.5 text-ink-muted">
                        {String(item.name || item.title || item.summary || item.id)}
                      </p>
                    ))}
                  </div>
                ))}
              </div>
            )}
          </div>
          <div className="flex items-center gap-3 font-mono text-[11px] text-ink-faint">
            <span className="inline-flex items-center gap-1.5 rounded-full border border-canvas-border bg-canvas-elevated/70 px-2.5 py-1">
              <span className="h-1.5 w-1.5 animate-pulseDot rounded-full bg-accent-good" />
              local
            </span>
            <span className="hidden sm:inline">NSE · BSE</span>
          </div>
        </header>
        <main className="flex-1 bg-grid bg-[length:56px_56px] p-6 md:p-8">{children}</main>
      </div>
    </div>
  );
}
