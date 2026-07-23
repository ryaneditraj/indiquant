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

function apiBase(): string {
  return process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
}

export async function fetchHealth(): Promise<HealthResponse | null> {
  try {
    const res = await fetch(`${apiBase()}/api/v1/health`, {
      next: { revalidate: 5 },
    });
    if (!res.ok) return null;
    return (await res.json()) as HealthResponse;
  } catch {
    return null;
  }
}

export async function fetchDashboard(): Promise<DashboardSnapshot | null> {
  try {
    const res = await fetch(`${apiBase()}/api/v1/dashboard/snapshot`, {
      next: { revalidate: 5 },
    });
    if (!res.ok) return null;
    return (await res.json()) as DashboardSnapshot;
  } catch {
    return null;
  }
}

export async function fetchNav(): Promise<{ app_name: string; sections: NavSection[] } | null> {
  try {
    const res = await fetch(`${apiBase()}/api/v1/meta/nav`, {
      next: { revalidate: 60 },
    });
    if (!res.ok) return null;
    return (await res.json()) as { app_name: string; sections: NavSection[] };
  } catch {
    return null;
  }
}

export async function fetchPublicSettings(): Promise<Record<string, unknown> | null> {
  try {
    const res = await fetch(`${apiBase()}/api/v1/settings/public`, {
      next: { revalidate: 30 },
    });
    if (!res.ok) return null;
    const body = (await res.json()) as { settings: Record<string, unknown> };
    return body.settings;
  } catch {
    return null;
  }
}
