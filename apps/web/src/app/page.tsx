import { MetricCard, SectionTitle } from "@/components/ui";
import { fetchDashboard, fetchHealth } from "@/lib/api";

export default async function DashboardPage() {
  const [health, snap] = await Promise.all([fetchHealth(), fetchDashboard()]);
  const online = Boolean(health?.status === "ok");

  return (
    <div className="mx-auto max-w-6xl space-y-8">
      <div>
        <p className="text-[11px] uppercase tracking-[0.2em] text-accent">Live cockpit</p>
        <h1 className="mt-2 font-display text-4xl tracking-tight text-ink">
          {snap?.app_name || health?.app_name || process.env.NEXT_PUBLIC_APP_NAME || "Research OS"}
        </h1>
        <p className="mt-2 max-w-2xl text-sm text-ink-muted">
          Continuous discovery laboratory for Indian markets. Hypotheses first. Validation always.
          Nothing hardcoded — configure providers in Settings.
        </p>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          label="API"
          value={online ? "online" : "offline"}
          hint={online ? `v${health?.version}` : "Start apps/api · uvicorn"}
          delay={0.05}
        />
        <MetricCard
          label="Queued experiments"
          value={snap?.queued_experiments ?? "—"}
          hint="Celery workers not started"
          delay={0.1}
        />
        <MetricCard
          label="Market regime"
          value={snap?.market_regime ?? "—"}
          hint="Classifier lands in Phase 4"
          delay={0.15}
        />
        <MetricCard
          label="Research score"
          value={snap?.research_score ?? 0}
          hint="Accepted edges / total tests"
          delay={0.2}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <section className="panel p-5 lg:col-span-2">
          <SectionTitle title="AI tasks" subtitle="CEO agent coordinates the research loop" />
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
                  </p>
                </div>
              </li>
            ))}
            {!snap?.ai_tasks?.length && (
              <li className="text-sm text-ink-muted">No live tasks — enable AI loop in config when ready.</li>
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
              <dd className="text-ink">{snap?.data_freshness ?? "—"}</dd>
            </div>
            <div className="flex justify-between gap-2">
              <dt className="text-ink-faint">market</dt>
              <dd className="text-ink">{health?.primary_market ?? "IN"}</dd>
            </div>
          </dl>
        </section>
      </div>

      <section className="panel p-5">
        <SectionTitle title="Timeline" subtitle="Recent research OS events" />
        <ol className="space-y-3">
          {(snap?.timeline || []).map((item, i) => (
            <li key={i} className="flex gap-4 text-sm">
              <span className="w-24 shrink-0 font-mono text-[11px] text-ink-faint">
                {String(item.ts)}
              </span>
              <div>
                <p className="text-ink">{String(item.event)}</p>
                <p className="text-ink-muted">{String(item.detail)}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>
    </div>
  );
}
