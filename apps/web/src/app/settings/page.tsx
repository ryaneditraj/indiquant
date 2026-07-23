import { SectionTitle } from "@/components/ui";
import { fetchPublicSettings } from "@/lib/api";

export default async function SettingsPage() {
  const settings = await fetchPublicSettings();

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <p className="text-[11px] uppercase tracking-[0.2em] text-accent">Configuration</p>
        <h1 className="mt-2 font-display text-3xl text-ink">Settings</h1>
        <p className="mt-2 text-sm text-ink-muted">
          Non-secret runtime snapshot from <code className="font-mono text-accent">config.yaml</code>{" "}
          + environment. Secrets never leave the API. Edit{" "}
          <code className="font-mono text-accent">.env</code> and config — never source — to change
          providers.
        </p>
      </div>

      <section className="panel p-5">
        <SectionTitle title="Public configuration" subtitle="Safe to display in the UI" />
        {!settings ? (
          <p className="text-sm text-accent-warn">
            API unreachable. Start the backend and set NEXT_PUBLIC_API_BASE_URL.
          </p>
        ) : (
          <pre className="overflow-x-auto rounded-lg bg-canvas p-4 font-mono text-xs leading-relaxed text-ink-muted">
            {JSON.stringify(settings, null, 2)}
          </pre>
        )}
      </section>

      <section className="panel p-5">
        <SectionTitle title="Where to configure" />
        <ul className="space-y-2 text-sm text-ink-muted">
          <li>
            <span className="text-ink">.env</span> — secrets, DATABASE_URL, AI keys, provider URLs
          </li>
          <li>
            <span className="text-ink">config.yaml</span> — defaults, feature flags, plugin module paths
          </li>
          <li>
            <span className="text-ink">Settings UI</span> — runtime overrides (persistence in Phase 1+)
          </li>
        </ul>
      </section>
    </div>
  );
}
