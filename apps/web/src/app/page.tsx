import Link from "next/link";

import { MetricCard, SectionTitle } from "@/components/ui";
import { fetchDashboard, fetchHealth } from "@/lib/api";

export default async function DashboardPage() {
  const [health, snap] = await Promise.all([fetchHealth(), fetchDashboard()]);
  const online = Boolean(health?.status === "ok");
  const name =
    snap?.app_name || health?.app_name || process.env.NEXT_PUBLIC_APP_NAME || "Pramana";

  return (
    <div className="mx-auto max-w-6xl space-y-8">
      <section className="relative overflow-hidden rounded-3xl border border-canvas-border bg-canvas-elevated/50 p-7 md:p-9">
        <div className="pointer-events-none absolute -right-16 -top-20 h-56 w-56 rounded-full bg-accent/10 blur-3xl" />
        <div className="pointer-events-none absolute bottom-0 left-1/3 h-40 w-40 rounded-full bg-accent-teal/10 blur-3xl" />
        <p className="text-[11px] uppercase tracking-[0.24em] text-accent">Live research cockpit</p>
        <h1 className="mt-3 max-w-3xl font-display text-4xl tracking-tight text-ink md:text-5xl">
          <span className="text-gradient">{name}</span>
        </h1>
        <p className="mt-3 max-w-2xl text-sm leading-relaxed text-ink-muted md:text-[15px]">
          Open-source AI quant research OS for Indian markets. Invent hypotheses, run rigorous
          validation, reject weak edges — continuously.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link
            href="/ai-lab"
            className="rounded-xl bg-accent px-4 py-2 text-sm font-medium text-canvas transition hover:brightness-110"
          >
            Start research loop
          </Link>
          <Link
            href="/research"
            className="rounded-xl border border-canvas-border bg-canvas/50 px-4 py-2 text-sm text-ink transition hover:border-accent/40"
          >
            Run single cycle
          </Link>
          <Link
            href="/settings"
            className="rounded-xl border border-transparent px-4 py-2 text-sm text-ink-muted transition hover:text-ink"
          >
            Configure providers
          </Link>
        </div>
      </section>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          label="API"
          value={online ? "online" : "offline"}
          hint={online ? `v${health?.version}` : "Start apps/api · uvicorn"}
          delay={0.05}
        />
        <MetricCard
          label="Queued"
          value={snap?.queued_experiments ?? "—"}
          hint="Experiments waiting"
          delay={0.1}
        />
        <MetricCard
          label="Market regime"
          value={String(snap?.market_regime ?? "—").replaceAll("_", " ")}
          hint="Live classifier"
          delay={0.15}
        />
        <MetricCard
          label="Research score"
          value={snap?.research_score ?? 0}
          hint="Accepted / tested"
          delay={0.2}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <section className="panel p-5 lg:col-span-2">
          <SectionTitle title="AI tasks" subtitle="CEO agent coordinates the discovery loop" />
          <ul className="space-y-3">
            {(snap?.ai_tasks || []).map((task, i) => (
              <li
                key={String(task.id ?? i)}
                className="flex items-start justify-between gap-3 border-b border-canvas-border/80 pb-3 last:border-0 last:pb-0"
              >
                <div>
                  <p className="text-sm text-ink">{String(task.title)}</p>
                  <p className="mt-0.5 font-mono text-[11px] text-ink-faint">
                    agent:{String(task.agent)} · {String(task.status)}
                    {task.cycles != null ? ` · cycles ${String(task.cycles)}` : ""}
                  </p>
                </div>
              </li>
            ))}
            {!snap?.ai_tasks?.length && (
              <li className="text-sm text-ink-muted">
                Idle. Open <Link className="text-accent" href="/ai-lab">AI Lab</Link> to start.
              </li>
            )}
          </ul>
        </section>

        <section className="panel p-5">
          <SectionTitle title="System health" />
          <dl className="space-y-2 font-mono text-xs">
            {Object.entries(snap?.system_health || { api: online ? "ok" : "down" }).map(
              ([key, value]) => (
                <div key={key} className="flex justify-between gap-2">
                  <dt className="text-ink-faint">{key}</dt>
                  <dd className="text-ink">{String(value)}</dd>
                </div>
              ),
            )}
            <div className="flex justify-between gap-2 pt-2">
              <dt className="text-ink-faint">data_freshness</dt>
              <dd className="truncate text-ink">{snap?.data_freshness ?? "—"}</dd>
            </div>
            <div className="flex justify-between gap-2">
              <dt className="text-ink-faint">market</dt>
              <dd className="text-ink">{health?.primary_market ?? "IN"}</dd>
            </div>
          </dl>
        </section>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <section className="panel p-5">
          <SectionTitle title="Recent discoveries" />
          <ul className="space-y-3">
            {(snap?.recent_discoveries || []).map((d, i) => (
              <li key={String(d.experiment_id ?? i)} className="text-sm">
                <p className="text-ink">{String(d.summary || "—")}</p>
                <p className="mt-0.5 font-mono text-[10px] text-ink-faint">
                  {String(d.status)} · {String(d.experiment_id)}
                </p>
              </li>
            ))}
            {!snap?.recent_discoveries?.length && (
              <li className="text-sm text-ink-muted">No discoveries yet — run a research cycle.</li>
            )}
          </ul>
        </section>

        <section className="panel p-5">
          <SectionTitle title="Timeline" subtitle="Recent events" />
          <ol className="space-y-3">
            {(snap?.timeline || []).map((item, i) => (
              <li key={i} className="flex gap-4 text-sm">
                <span className="w-28 shrink-0 truncate font-mono text-[10px] text-ink-faint">
                  {String(item.ts).slice(0, 19)}
                </span>
                <div>
                  <p className="text-ink">{String(item.event)}</p>
                  <p className="text-ink-muted">{String(item.detail)}</p>
                </div>
              </li>
            ))}
            {!snap?.timeline?.length && (
              <li className="text-sm text-ink-muted">Timeline fills as experiments land.</li>
            )}
          </ol>
        </section>
      </div>
    </div>
  );
}
