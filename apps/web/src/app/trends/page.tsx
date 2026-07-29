"use client";

import { useCallback, useEffect, useState } from "react";

import { ActionButton } from "@/components/ActionButton";
import { ComponentBars, RegionHeatBars, TrendsDualLine } from "@/components/TrendsChart";
import { MetricCard, SectionTitle } from "@/components/ui";
import { apiBase } from "@/lib/api";

type EntityInfo = {
  entity_id: string;
  label?: string;
  ticker?: string | null;
};

type CrossChannel = {
  label?: string;
  source?: string;
  corr_with_search?: number | null;
  divergence?: number | null;
  latest?: number | null;
};

type Dashboard = {
  ok?: boolean;
  error?: string;
  entity_id?: string;
  label?: string;
  ticker?: string;
  empty_state?: boolean;
  next_steps?: string[];
  inventory?: Record<string, number | string>;
  score?: {
    search_demand_score?: number;
    quality_badge?: string;
    regime?: string;
    regime_reason?: string;
    components?: Record<string, number>;
    confidence_interval?: { low: number; high: number };
    chart?: {
      brand: Array<{ date: string; interest: number }>;
      transactional: Array<{ date: string; interest: number }>;
    };
    heatmap?: Array<{ region: string; interest: number }>;
    rising_queries?: Array<{ query: string; value: number }>;
    features?: Record<string, unknown>;
    caveats?: string[];
  };
  alerts?: Array<{
    kind: string;
    direction: string;
    magnitude: number;
    confidence: string;
    explanation: string;
    query_group: string;
  }>;
  pre_earnings?: {
    next_earnings_date?: string;
    days_to_earnings?: number;
    search_surprise_vs_trailing?: number | null;
    classification?: string;
    confidence_interval?: { low: number; high: number };
    historical_pre_earnings?: Array<{
      earnings_date: string;
      score_14d_before: number;
      regime: string;
      quality_badge: string;
    }>;
  };
  cross_signal?: {
    note?: string;
    search_confirmation_composite?: number | null;
    panel?: Record<string, CrossChannel>;
  };
  caveats?: string[];
};

type RankingRow = {
  entity_id: string;
  label?: string;
  ticker?: string | null;
  rank?: number;
  ranking_score?: number;
  search_demand_score?: number;
  quality_badge?: string;
  regime?: string;
  side_hint?: string;
  model_ready?: boolean;
  ranking_method?: string;
};

type ModelPred = {
  ok?: boolean;
  error?: string;
  quality_badge?: string;
  ranking_score?: number;
  proxy_note?: string;
  predictions?: {
    revenue_growth?: { value: number; confidence_interval?: { low: number; high: number } };
    sss_proxy?: { value: number; confidence_interval?: { low: number; high: number } };
    beat_inline_miss?: { class?: string; probabilities?: Record<string, number> };
    nowcast_momentum?: { value: number; confidence_interval?: { low: number; high: number } };
  };
};

function badgeClass(b?: string) {
  if (b === "high") return "text-accent-good";
  if (b === "medium") return "text-accent-warn";
  if (b === "low") return "text-accent-radar";
  return "text-accent-bad";
}

function fmt(n: unknown, digits = 2) {
  if (n == null || n === "") return "—";
  const v = Number(n);
  if (Number.isNaN(v)) return String(n);
  return v.toFixed(digits);
}

export default function TrendsPage() {
  const [entities, setEntities] = useState<EntityInfo[]>([]);
  const [entityId, setEntityId] = useState("dmart");
  const [dash, setDash] = useState<Dashboard | null>(null);
  const [backtest, setBacktest] = useState<Record<string, unknown> | null>(null);
  const [rankings, setRankings] = useState<RankingRow[]>([]);
  const [model, setModel] = useState<ModelPred | null>(null);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState<"entity" | "comparison">("entity");

  const refreshEntities = useCallback(async () => {
    try {
      const res = await fetch(`${apiBase()}/api/v1/trends/entities`);
      if (!res.ok) return;
      const body = await res.json();
      const list = (body.entities || []) as EntityInfo[];
      setEntities(list);
      if (list.length && !list.some((e) => e.entity_id === entityId)) {
        setEntityId(list[0].entity_id);
      }
    } catch {
      /* ignore */
    }
  }, [entityId]);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${apiBase()}/api/v1/trends/${entityId}/dashboard`);
      const body = res.ok ? await res.json() : { ok: false, error: `HTTP ${res.status}` };
      setDash(body);
      const pred = await fetch(`${apiBase()}/api/v1/trends/${entityId}/predict`);
      if (pred.ok) setModel(await pred.json());
      else setModel(null);
    } catch {
      setDash({ ok: false, error: "API unreachable" });
    } finally {
      setLoading(false);
    }
  }, [entityId]);

  const refreshComparison = useCallback(async () => {
    try {
      const res = await fetch(`${apiBase()}/api/v1/trends/comparison`);
      if (!res.ok) return;
      const body = await res.json();
      setRankings((body.rankings || []) as RankingRow[]);
    } catch {
      /* ignore */
    }
  }, []);

  useEffect(() => {
    refreshEntities();
  }, [refreshEntities]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    if (view === "comparison") refreshComparison();
  }, [view, refreshComparison]);

  const score = dash?.score;
  const components = score?.components || {};
  const activeLabel =
    dash?.label || entities.find((e) => e.entity_id === entityId)?.label || entityId;
  const crossPanel = dash?.cross_signal?.panel || {};

  async function downloadExport() {
    const res = await fetch(`${apiBase()}/api/v1/trends/${entityId}/export`);
    if (!res.ok) return;
    const json = await res.json();
    const blob = new Blob([JSON.stringify(json, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `trends-${entityId}-export.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div>
        <p className="text-[11px] uppercase tracking-[0.2em] text-accent">Alt-data · Google Trends</p>
        <h1 className="mt-2 font-display text-3xl text-ink">Retail Search Intelligence</h1>
        <p className="mt-2 max-w-3xl text-sm text-ink-muted">
          Pre-earnings search demand layer across India retail / consumer names. Trends is a sampled,
          relative 0–100 index — never absolute volume. Confirmatory channel alongside satellite, app,
          pricing, and hiring signals.
        </p>
      </div>

      <section className="panel border-accent-warn/30 p-4">
        <p className="text-[11px] uppercase tracking-[0.16em] text-accent-warn">Non-negotiable</p>
        <ul className="mt-2 space-y-1 text-xs text-ink-muted">
          {(
            dash?.caveats ||
            dash?.score?.caveats || [
              "Google Trends is relative 0–100 within window/geography — not absolute search volume.",
              "Separate exports are not comparable without shared anchors or comparison-group context.",
            ]
          )
            .slice(0, 4)
            .map((c) => (
              <li key={c}>· {c}</li>
            ))}
        </ul>
      </section>

      <section className="panel p-5">
        <SectionTitle title="Universe" subtitle="Entity switcher · Phase 2 multi-name" />
        <div className="flex flex-wrap items-center gap-3">
          <label className="text-xs text-ink-faint">
            Entity
            <select
              className="ml-2 rounded-xl border border-canvas-border bg-canvas/60 px-3 py-2 text-sm text-ink"
              value={entityId}
              onChange={(e) => setEntityId(e.target.value)}
            >
              {(entities.length ? entities : [{ entity_id: "dmart", label: "DMart" }]).map((e) => (
                <option key={e.entity_id} value={e.entity_id}>
                  {e.label || e.entity_id}
                  {e.ticker ? ` · ${e.ticker}` : ""}
                </option>
              ))}
            </select>
          </label>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setView("entity")}
              className={`rounded-xl border px-3 py-2 text-xs ${
                view === "entity" ? "border-accent/50 text-accent" : "border-canvas-border text-ink-muted"
              }`}
            >
              Entity dashboard
            </button>
            <button
              type="button"
              onClick={() => setView("comparison")}
              className={`rounded-xl border px-3 py-2 text-xs ${
                view === "comparison"
                  ? "border-accent/50 text-accent"
                  : "border-canvas-border text-ink-muted"
              }`}
            >
              Multi-entity ranking
            </button>
          </div>
        </div>
      </section>

      <section className="panel p-5">
        <SectionTitle title="Collection" subtitle="Fixture offline by default · optional pytrends live" />
        <div className="flex flex-wrap gap-3">
          <ActionButton
            label={`Collect ${activeLabel} (fixture)`}
            path="/api/v1/trends/collect"
            demo
            body={{ entity_id: entityId, provider: "fixture" }}
          />
          <ActionButton
            label="Collect all entities"
            path="/api/v1/trends/collect-all"
            demo
            body={{}}
          />
          <ActionButton label="Train models (proxy labels)" path="/api/v1/trends/models/train" demo body={{}} />
          <button
            type="button"
            onClick={() => {
              refresh();
              if (view === "comparison") refreshComparison();
            }}
            className="rounded-xl border border-canvas-border px-4 py-2 text-sm text-ink hover:border-accent/40"
          >
            Refresh
          </button>
          <button
            type="button"
            onClick={async () => {
              const res = await fetch(`${apiBase()}/api/v1/trends/${entityId}/backtest`, {
                method: "POST",
              });
              setBacktest(res.ok ? await res.json() : { ok: false });
            }}
            className="rounded-xl border border-canvas-border px-4 py-2 text-sm text-ink hover:border-accent/40"
          >
            PIT pre-earnings backtest
          </button>
          <button
            type="button"
            onClick={downloadExport}
            className="rounded-xl border border-canvas-border px-4 py-2 text-sm text-ink hover:border-accent/40"
          >
            Export score JSON
          </button>
        </div>
      </section>

      {view === "comparison" && (
        <section className="panel p-5">
          <SectionTitle
            title="Retail longs / shorts ranking"
            subtitle="Proxy-trained ranking · relative search demand — not absolute volume · not trade advice"
          />
          <div className="overflow-hidden rounded-xl border border-canvas-border">
            <table className="w-full text-left text-xs">
              <thead className="bg-canvas/60 text-ink-faint">
                <tr>
                  <th className="px-3 py-2">Rank</th>
                  <th className="px-3 py-2">Entity</th>
                  <th className="px-3 py-2">Score</th>
                  <th className="px-3 py-2">Demand</th>
                  <th className="px-3 py-2">Regime</th>
                  <th className="px-3 py-2">Quality</th>
                  <th className="px-3 py-2">Method</th>
                  <th className="px-3 py-2">Side</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-canvas-border">
                {rankings.map((r) => (
                  <tr
                    key={r.entity_id}
                    className="cursor-pointer hover:bg-canvas/40"
                    onClick={() => {
                      setEntityId(r.entity_id);
                      setView("entity");
                    }}
                  >
                    <td className="px-3 py-2 font-mono text-ink">{r.rank ?? "—"}</td>
                    <td className="px-3 py-2 text-ink">
                      {r.label || r.entity_id}
                      {r.ticker ? (
                        <span className="ml-2 font-mono text-[10px] text-ink-faint">{r.ticker}</span>
                      ) : null}
                    </td>
                    <td className="px-3 py-2 font-mono text-ink">{fmt(r.ranking_score)}</td>
                    <td className="px-3 py-2 font-mono text-ink">{fmt(r.search_demand_score)}</td>
                    <td className="px-3 py-2 capitalize text-ink-muted">{r.regime}</td>
                    <td className={`px-3 py-2 ${badgeClass(r.quality_badge)}`}>{r.quality_badge}</td>
                    <td className="px-3 py-2 font-mono text-[10px] text-ink-faint">
                      {r.ranking_method || (r.model_ready ? "model" : "—")}
                    </td>
                    <td
                      className={`px-3 py-2 capitalize ${
                        r.side_hint === "watch" ? "text-accent-warn" : "text-accent-radar"
                      }`}
                    >
                      {r.side_hint}
                    </td>
                  </tr>
                ))}
                {!rankings.length && (
                  <tr>
                    <td colSpan={8} className="px-3 py-8 text-center">
                      <p className="text-sm text-ink">No rankings yet</p>
                      <p className="mt-2 text-xs text-ink-muted">
                        Fresh clone? Seed fixture Trends data, then open this view again.
                      </p>
                      <ol className="mx-auto mt-3 max-w-md space-y-1 text-left text-xs text-ink-muted">
                        <li>1. In the repo root: <code className="text-accent">make trends-demo</code></li>
                        <li>2. Click <span className="text-ink">Collect all entities</span> or refresh</li>
                        <li>3. Optional: <code className="text-accent">make trends-train</code> for model ranks</li>
                      </ol>
                      <p className="mt-3 text-[10px] text-ink-faint">
                        Rankings are relative tertiles on proxy scores — not buy/sell advice.
                      </p>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {view === "entity" && loading && <p className="text-sm text-ink-muted">Loading Trends dashboard…</p>}

      {view === "entity" && !loading && dash && !dash.ok && (
        <section className="panel border-accent-warn/25 p-6">
          <p className="text-[11px] uppercase tracking-[0.16em] text-accent-warn">Empty state</p>
          <h2 className="mt-2 font-display text-2xl text-ink">No Trends inventory yet</h2>
          <p className="mt-2 max-w-xl text-sm text-ink-muted">
            {dash.error || "Collect fixture (or live) Trends data before the dashboard can score demand."}
          </p>
          <ol className="mt-4 space-y-2 text-sm text-ink-muted">
            {(
              dash.next_steps || [
                "make trends-demo  # fixture offline seed for dmart + trent",
                "Click Collect above, then Refresh",
                "Optional: make trends-train for proxy model ranking",
              ]
            ).map((step) => (
              <li key={step} className="flex gap-2">
                <span className="font-mono text-accent">→</span>
                <code className="text-xs text-ink">{step}</code>
              </li>
            ))}
          </ol>
          <div className="mt-5 flex flex-wrap gap-3">
            <ActionButton
              label={`Collect ${activeLabel} (fixture)`}
              path="/api/v1/trends/collect"
              demo
              body={{ entity_id: entityId, provider: "fixture" }}
            />
            <button
              type="button"
              onClick={() => refresh()}
              className="rounded-xl border border-canvas-border px-4 py-2 text-sm text-ink hover:border-accent/40"
            >
              Refresh after collect
            </button>
          </div>
          <p className="mt-4 text-[11px] text-ink-faint">
            Inventory: {JSON.stringify(dash.inventory || {})} · Never absolute volume
          </p>
          {dash.caveats?.length ? (
            <ul className="mt-3 space-y-1 text-[11px] text-ink-faint">
              {dash.caveats.slice(0, 3).map((c) => (
                <li key={c}>· {c}</li>
              ))}
            </ul>
          ) : null}
        </section>
      )}

      {view === "entity" && dash?.ok && score && (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <MetricCard
              label="Search Demand Score"
              value={score.search_demand_score ?? "—"}
              hint={`CI ${score.confidence_interval?.low ?? "—"}–${score.confidence_interval?.high ?? "—"}`}
            />
            <MetricCard label="Regime" value={String(score.regime || "—")} hint={score.regime_reason} />
            <MetricCard
              label="Signal quality"
              value={String(score.quality_badge || "—")}
              hint="high · medium · low · unreliable"
            />
            <MetricCard
              label="Days to earnings"
              value={dash.pre_earnings?.days_to_earnings ?? "—"}
              hint={dash.pre_earnings?.next_earnings_date || "calendar"}
            />
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <section className="panel p-5">
              <SectionTitle title="Brand vs transactional" subtitle="Shared-window relative indices" />
              <TrendsDualLine
                brand={score.chart?.brand || []}
                transactional={score.chart?.transactional || []}
              />
            </section>
            <section className="panel p-5">
              <SectionTitle title="Score decomposition" subtitle="Interpretable subcomponents" />
              <ComponentBars components={components} />
              <p className={`mt-2 text-xs ${badgeClass(score.quality_badge)}`}>
                Quality badge: {score.quality_badge}
              </p>
            </section>
          </div>

          <section className="panel p-5">
            <SectionTitle
              title="Model outputs"
              subtitle="Gradient boosting on Trends features · proxy labels until fundamentals wired"
            />
            {model?.ok ? (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <div>
                  <p className="text-[11px] uppercase text-ink-faint">Rev growth proxy %</p>
                  <p className="mt-1 font-mono text-xl text-ink">
                    {fmt(model.predictions?.revenue_growth?.value)}
                  </p>
                  <p className="text-[10px] text-ink-faint">
                    CI {fmt(model.predictions?.revenue_growth?.confidence_interval?.low)}–
                    {fmt(model.predictions?.revenue_growth?.confidence_interval?.high)}
                  </p>
                </div>
                <div>
                  <p className="text-[11px] uppercase text-ink-faint">SSS proxy %</p>
                  <p className="mt-1 font-mono text-xl text-ink">
                    {fmt(model.predictions?.sss_proxy?.value)}
                  </p>
                </div>
                <div>
                  <p className="text-[11px] uppercase text-ink-faint">Beat / inline / miss</p>
                  <p className="mt-1 font-display text-2xl capitalize text-ink">
                    {model.predictions?.beat_inline_miss?.class || "—"}
                  </p>
                </div>
                <div>
                  <p className="text-[11px] uppercase text-ink-faint">Nowcast momentum</p>
                  <p className="mt-1 font-mono text-xl text-ink">
                    {fmt(model.predictions?.nowcast_momentum?.value, 3)}
                  </p>
                  <p className={`text-xs ${badgeClass(model.quality_badge)}`}>{model.quality_badge}</p>
                </div>
              </div>
            ) : (
              <p className="text-sm text-ink-muted">
                {model?.error || "Train models to unlock predictions (POST /trends/models/train)."}
              </p>
            )}
            <p className="mt-3 text-[11px] text-ink-faint">
              {model?.proxy_note ||
                "Proxy targets derived from score regimes + noise — not filed financials."}
            </p>
          </section>

          <div className="grid gap-4 lg:grid-cols-2">
            <section className="panel p-5">
              <SectionTitle title="India regional strength" subtitle="Interest by state (relative)" />
              <RegionHeatBars regions={score.heatmap || []} />
            </section>
            <section className="panel p-5">
              <SectionTitle title="Rising related queries" subtitle="Independent signal channel" />
              <ul className="max-h-64 space-y-2 overflow-auto">
                {(score.rising_queries || []).map((q) => (
                  <li key={q.query} className="flex justify-between gap-3 text-sm">
                    <span className="text-ink">{q.query}</span>
                    <span className="font-mono text-xs text-accent-radar">+{q.value}</span>
                  </li>
                ))}
                {!score.rising_queries?.length && (
                  <li className="text-sm text-ink-muted">No rising queries in store.</li>
                )}
              </ul>
            </section>
          </div>

          <section className="panel p-5">
            <SectionTitle title="Pre-earnings panel" subtitle="Point-in-time search momentum" />
            <div className="grid gap-4 md:grid-cols-3">
              <div>
                <p className="text-[11px] uppercase text-ink-faint">Classification</p>
                <p className="mt-1 font-display text-2xl capitalize text-ink">
                  {dash.pre_earnings?.classification || score.regime}
                </p>
              </div>
              <div>
                <p className="text-[11px] uppercase text-ink-faint">Search surprise vs trail</p>
                <p className="mt-1 font-mono text-xl text-ink">
                  {dash.pre_earnings?.search_surprise_vs_trailing ?? "—"}
                </p>
              </div>
              <div>
                <p className="text-[11px] uppercase text-ink-faint">Risk / friction ratio</p>
                <p className="mt-1 font-mono text-xl text-ink">
                  {String(score.features?.risk_query_ratio ?? "—")}
                </p>
              </div>
            </div>
            <div className="mt-4 overflow-hidden rounded-xl border border-canvas-border">
              <table className="w-full text-left text-xs">
                <thead className="bg-canvas/60 text-ink-faint">
                  <tr>
                    <th className="px-3 py-2">Earnings</th>
                    <th className="px-3 py-2">Score @ T−14</th>
                    <th className="px-3 py-2">Regime</th>
                    <th className="px-3 py-2">Quality</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-canvas-border">
                  {(dash.pre_earnings?.historical_pre_earnings || []).map((h) => (
                    <tr key={h.earnings_date}>
                      <td className="px-3 py-2 font-mono text-ink">{h.earnings_date}</td>
                      <td className="px-3 py-2 font-mono text-ink">{h.score_14d_before}</td>
                      <td className="px-3 py-2 capitalize text-ink-muted">{h.regime}</td>
                      <td className={`px-3 py-2 ${badgeClass(h.quality_badge)}`}>{h.quality_badge}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="panel p-5">
            <SectionTitle title="Alerts" subtitle="Direction · magnitude · confidence · NL explanation" />
            <ul className="space-y-3">
              {(dash.alerts || []).map((a) => (
                <li
                  key={`${a.kind}-${a.magnitude}`}
                  className="rounded-xl border border-canvas-border/80 px-4 py-3"
                >
                  <div className="flex flex-wrap items-center gap-2 text-sm">
                    <span className="font-mono text-accent">{a.kind}</span>
                    <span className="text-ink-faint">·</span>
                    <span className="capitalize text-ink">{a.direction}</span>
                    <span className="font-mono text-xs text-ink-muted">mag {a.magnitude}</span>
                    <span className={`text-xs ${badgeClass(a.confidence)}`}>{a.confidence}</span>
                    <span className="font-mono text-[10px] text-ink-faint">{a.query_group}</span>
                  </div>
                  <p className="mt-1 text-sm text-ink-muted">{a.explanation}</p>
                </li>
              ))}
              {!dash.alerts?.length && (
                <li className="text-sm text-ink-muted">No threshold breaches on current features.</li>
              )}
            </ul>
          </section>

          <section className="panel p-5">
            <SectionTitle
              title="Cross-signal panel"
              subtitle={`Confirmation composite ${fmt(dash.cross_signal?.search_confirmation_composite, 3)} · fixture adapters offline`}
            />
            <p className="mb-3 text-sm text-ink-muted">{dash.cross_signal?.note}</p>
            <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
              {(["satellite", "app_rank", "pricing_promo", "hiring"] as const).map((key) => {
                const ch = crossPanel[key] || {};
                return (
                  <div
                    key={key}
                    className="rounded-xl border border-canvas-border px-3 py-4 text-center text-xs"
                  >
                    <div className="text-ink">{ch.label || key}</div>
                    <div className="mt-2 font-mono text-lg text-ink">{fmt(ch.latest)}</div>
                    <div className="mt-1 text-ink-muted">corr {fmt(ch.corr_with_search)}</div>
                    <div className="text-ink-faint">div {fmt(ch.divergence)}</div>
                    <div className="mt-1 text-[10px] uppercase tracking-wide text-ink-faint">
                      {ch.source || "fixture"}
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        </>
      )}

      {backtest && (
        <section className="panel p-5">
          <SectionTitle title="PIT backtest result" subtitle="as_of strictly before earnings" />
          <pre className="max-h-80 overflow-auto rounded-xl bg-canvas/80 p-4 font-mono text-[11px] text-ink-muted">
            {JSON.stringify(backtest, null, 2)}
          </pre>
        </section>
      )}
    </div>
  );
}
