"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";

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
  { id: "logs", label: "Logs", href: "/logs" },
  { id: "settings", label: "Settings", href: "/settings" },
  { id: "docs", label: "Documentation", href: "/docs" },
];

const appName = process.env.NEXT_PUBLIC_APP_NAME || "Research OS";

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

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
        <p className="px-2 pt-4 font-mono text-[10px] text-ink-faint">⌘K search · Phase 0</p>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-20 flex h-12 items-center justify-between border-b border-canvas-border bg-canvas/70 px-6 backdrop-blur-md">
          <p className="text-sm text-ink-muted">
            Discover · validate · organize —{" "}
            <span className="text-ink">evidence over intuition</span>
          </p>
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
