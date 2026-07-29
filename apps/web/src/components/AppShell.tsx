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
  { id: "trends", label: "Trends", href: "/trends" },
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

const appName = process.env.NEXT_PUBLIC_APP_NAME || "Indiquant";
const parentBrand = process.env.NEXT_PUBLIC_PARENT_BRAND || "Money Radar";
const parentUrl = process.env.NEXT_PUBLIC_PARENT_URL || "https://moneyradar.in";
const orgName = process.env.NEXT_PUBLIC_ORG_NAME || "Thugir Group";

type StatusKind = "online" | "offline" | "loop";

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [query, setQuery] = useState("");
  const [hits, setHits] = useState<Record<string, unknown> | null>(null);
  const [status, setStatus] = useState<{ kind: StatusKind; label: string }>({
    kind: "offline",
    label: "connecting",
  });

  useEffect(() => {
    let alive = true;
    async function ping() {
      try {
        const [healthRes, loopRes] = await Promise.all([
          fetch(`${apiBase()}/api/v1/health`),
          fetch(`${apiBase()}/api/v1/ai/loop`),
        ]);
        if (!alive) return;
        if (!healthRes.ok) {
          setStatus({ kind: "offline", label: "offline" });
          return;
        }
        const loop = loopRes.ok ? await loopRes.json() : null;
        if (loop?.status === "running") {
          setStatus({ kind: "loop", label: "scanning" });
        } else if (loop?.status === "paused") {
          setStatus({ kind: "loop", label: "paused" });
        } else {
          setStatus({ kind: "online", label: "idle" });
        }
      } catch {
        if (alive) setStatus({ kind: "offline", label: "offline" });
      }
    }
    ping();
    const id = setInterval(ping, 4000);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, []);

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

  const dot =
    status.kind === "offline"
      ? "bg-accent-bad"
      : status.kind === "loop"
        ? "bg-accent animate-pulseDot"
        : "bg-accent-good";

  return (
    <div className="flex min-h-screen">
      <aside className="sticky top-0 flex h-screen w-[15.75rem] shrink-0 flex-col border-r border-canvas-border/90 bg-canvas/90 px-3 py-5 backdrop-blur-xl">
        <Link href="/" className="mb-6 flex items-center gap-3 px-2">
          <span className="brand-mark relative flex h-10 w-10 items-center justify-center rounded-2xl">
            <span className="absolute inset-1 rounded-xl border border-canvas/30" />
            <span className="relative h-2 w-2 rounded-full bg-canvas" />
          </span>
          <span>
            <span className="block font-display text-2xl leading-none tracking-tight text-ink">
              {appName}
            </span>
            <span className="mt-1 block text-[10px] uppercase tracking-[0.2em] text-accent-radar">
              by {parentBrand}
            </span>
          </span>
        </Link>

        <a
          href={parentUrl}
          target="_blank"
          rel="noreferrer"
          className="mx-1 mb-5 rounded-xl border border-canvas-border/80 bg-canvas-elevated/70 px-3 py-2 transition hover:border-accent/30"
        >
          <p className="font-mono text-[9px] uppercase tracking-[0.18em] text-ink-faint">Parent</p>
          <p className="text-sm font-medium text-accent">{parentBrand}</p>
          <p className="font-mono text-[10px] text-ink-muted">moneyradar.in</p>
        </a>

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
                    className="absolute inset-0 rounded-lg bg-accent-soft/90 ring-1 ring-accent/25"
                    transition={{ type: "spring", stiffness: 380, damping: 32 }}
                  />
                )}
                <span className="relative z-10">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="mt-3 space-y-2 px-1">
          <div className="rounded-xl border border-canvas-border/70 bg-canvas-elevated/50 p-3">
            <p className="font-mono text-[9px] uppercase tracking-[0.16em] text-ink-faint">Built by</p>
            <p className="mt-1 text-xs font-medium text-ink">{orgName}</p>
            <p className="mt-2 text-[10px] leading-relaxed text-ink-muted">
              Non-commercial open source. Proof before prediction.
            </p>
          </div>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-20 flex h-14 items-center justify-between gap-4 border-b border-canvas-border/80 bg-canvas/75 px-6 backdrop-blur-xl">
          <div className="relative min-w-0 max-w-lg flex-1">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search experiments, strategies, hypotheses…"
              className="w-full rounded-xl border border-canvas-border bg-canvas-elevated/80 px-3.5 py-2 text-sm text-ink outline-none transition focus:border-accent/40 focus:ring-1 focus:ring-accent/30"
            />
            {hits && (
              <div className="panel absolute left-0 right-0 top-11 z-30 max-h-72 overflow-auto p-3 text-xs">
                {(["strategies", "experiments", "hypotheses"] as const).map((key) => {
                  const items = (hits[key] as Array<Record<string, unknown>>) || [];
                  if (!items.length) return null;
                  return (
                    <div key={key} className="mb-2 last:mb-0">
                      <p className="mb-1 uppercase tracking-wider text-ink-faint">{key}</p>
                      {items.map((item) => {
                        const href =
                          key === "strategies"
                            ? `/strategies/${item.id}`
                            : key === "experiments"
                              ? "/experiments"
                              : "/research";
                        return (
                          <Link
                            key={String(item.id)}
                            href={href}
                            className="block truncate py-0.5 text-ink-muted hover:text-accent"
                            onClick={() => {
                              setQuery("");
                              setHits(null);
                            }}
                          >
                            {String(item.name || item.title || item.summary || item.id)}
                          </Link>
                        );
                      })}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
          <div className="flex items-center gap-2 font-mono text-[11px] text-ink-faint">
            <span className="inline-flex items-center gap-1.5 rounded-full border border-canvas-border bg-canvas-elevated/70 px-2.5 py-1">
              <span className={`h-1.5 w-1.5 rounded-full ${dot}`} />
              {status.label}
            </span>
            <span className="hidden rounded-full border border-canvas-border px-2.5 py-1 sm:inline">
              NSE · BSE
            </span>
          </div>
        </header>
        <main className="relative flex-1 bg-grid bg-[length:56px_56px] p-6 md:p-8">
          <div className="pointer-events-none absolute inset-0 radar-ring opacity-40" />
          <div className="relative">{children}</div>
        </main>
      </div>
    </div>
  );
}
