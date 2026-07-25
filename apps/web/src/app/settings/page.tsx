import Link from "next/link";

import { SectionTitle } from "@/components/ui";
import { fetchPublicSettings } from "@/lib/api";

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-start justify-between gap-4 border-b border-canvas-border/60 py-2.5 last:border-0">
      <dt className="shrink-0 text-xs uppercase tracking-[0.12em] text-ink-faint">{label}</dt>
      <dd className="text-right text-sm text-ink">{value}</dd>
    </div>
  );
}

export default async function SettingsPage() {
  const settings = await fetchPublicSettings();
  const ai = (settings?.ai || {}) as Record<string, unknown>;
  const features = (settings?.features || {}) as Record<string, unknown>;

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <p className="text-[11px] uppercase tracking-[0.2em] text-accent">Configuration</p>
        <h1 className="mt-2 font-display text-3xl text-ink">Settings</h1>
        <p className="mt-2 text-sm text-ink-muted">
          Public runtime snapshot. Secrets stay on the server — edit{" "}
          <code className="font-mono text-accent">.env</code> and{" "}
          <code className="font-mono text-accent">config.yaml</code> to change providers.
        </p>
      </div>

      {!settings ? (
        <section className="panel p-5">
          <p className="text-sm text-accent-warn">
            API unreachable. Start the backend and set{" "}
            <code className="font-mono">NEXT_PUBLIC_API_BASE_URL</code>.
          </p>
        </section>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          <section className="panel p-5">
            <SectionTitle title="Product" />
            <dl>
              <Row label="App" value={String(settings.app_name || "Indiquant")} />
              <Row label="Parent" value={String(settings.parent_brand || "Money Radar")} />
              <Row label="Org" value={String(settings.organization || "Thugir Group")} />
              <Row label="Market" value={String(settings.primary_market || "IN")} />
              <Row label="License" value={String(settings.license || "PolyForm NC")} />
              <Row label="Env" value={String(settings.env || "—")} />
            </dl>
          </section>

          <section className="panel p-5">
            <SectionTitle title="AI" />
            <dl>
              <Row label="Provider" value={String(ai.default_provider || "—")} />
              <Row label="Model" value={String(ai.default_model || "—")} />
              <Row
                label="API key"
                value={ai.has_openai_compatible_key ? "configured" : "missing"}
              />
            </dl>
          </section>

          <section className="panel p-5 md:col-span-2">
            <SectionTitle title="Feature flags" />
            <div className="flex flex-wrap gap-2">
              {Object.entries(features).map(([key, value]) => (
                <span
                  key={key}
                  className={`rounded-full border px-2.5 py-1 font-mono text-[11px] ${
                    value
                      ? "border-accent/30 bg-accent-soft text-accent"
                      : "border-canvas-border text-ink-faint"
                  }`}
                >
                  {key}: {String(value)}
                </span>
              ))}
            </div>
          </section>
        </div>
      )}

      <section className="panel p-5">
        <SectionTitle title="Where to configure" />
        <ul className="space-y-2 text-sm text-ink-muted">
          <li>
            <span className="text-ink">.env</span> — secrets, DATABASE_URL, AI keys, provider URLs
          </li>
          <li>
            <span className="text-ink">config.yaml</span> — branding, feature flags, plugin paths
          </li>
          <li>
            <span className="text-ink">Commercial license</span> —{" "}
            <a href="https://moneyradar.in" className="text-accent-radar hover:underline">
              moneyradar.in
            </a>
          </li>
        </ul>
        <p className="mt-4 text-xs text-ink-faint">
          Need a different default symbol set? Open{" "}
          <Link href="/research" className="text-accent">
            Research
          </Link>{" "}
          or{" "}
          <Link href="/ai-lab" className="text-accent">
            AI Lab
          </Link>
          .
        </p>
      </section>
    </div>
  );
}
