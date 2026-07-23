export type HealthResponse = {
  status: string;
  app_name: string;
  version: string;
  env: string;
  primary_market: string;
  database_configured: boolean;
  redis_configured: boolean;
  features: Record<string, unknown>;
};

export type DashboardSnapshot = {
  app_name: string;
  research_score: number;
  ai_tasks: Array<Record<string, unknown>>;
  queued_experiments: number;
  completed_experiments: number;
  rejected_strategies: number;
  top_strategies: Array<Record<string, unknown>>;
  market_regime: string;
  data_freshness: string;
  system_health: Record<string, unknown>;
  recent_discoveries: Array<Record<string, unknown>>;
  timeline: Array<Record<string, unknown>>;
};

export type NavSection = {
  id: string;
  label: string;
  href: string;
  enabled?: boolean;
};

export function apiBase(): string {
  return process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
}

async function getJson<T>(path: string, init?: RequestInit): Promise<T | null> {
  try {
    const res = await fetch(`${apiBase()}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers || {}),
      },
      next: init?.method && init.method !== "GET" ? undefined : { revalidate: 5 },
      cache: init?.method && init.method !== "GET" ? "no-store" : undefined,
    });
    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch {
    return null;
  }
}

export async function fetchHealth(): Promise<HealthResponse | null> {
  return getJson<HealthResponse>("/api/v1/health");
}

export async function fetchDashboard(): Promise<DashboardSnapshot | null> {
  return getJson<DashboardSnapshot>("/api/v1/dashboard/snapshot");
}

export async function fetchNav(): Promise<{ app_name: string; sections: NavSection[] } | null> {
  return getJson("/api/v1/meta/nav");
}

export async function fetchPublicSettings(): Promise<Record<string, unknown> | null> {
  const body = await getJson<{ settings: Record<string, unknown> }>("/api/v1/settings/public");
  return body?.settings ?? null;
}

export async function fetchExperiments() {
  return getJson<Array<Record<string, unknown>>>("/api/v1/experiments");
}

export async function fetchStrategies() {
  return getJson<Array<Record<string, unknown>>>("/api/v1/strategies");
}

export async function fetchHypotheses() {
  return getJson<Array<Record<string, unknown>>>("/api/v1/hypotheses");
}

export async function fetchDatasets() {
  return getJson<{ datasets: Array<Record<string, unknown>> }>("/api/v1/datasets");
}

export async function fetchProviders() {
  return getJson<{ providers: Array<Record<string, unknown>> }>("/api/v1/data/providers");
}

export async function fetchAuditLogs() {
  return getJson<{ events: Array<Record<string, unknown>> }>("/api/v1/logs/audit");
}

export async function fetchSearch(q: string) {
  return getJson<Record<string, unknown>>(`/api/v1/search?q=${encodeURIComponent(q)}`);
}
