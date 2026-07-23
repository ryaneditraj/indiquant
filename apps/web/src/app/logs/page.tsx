import { SectionTitle } from "@/components/ui";
import { fetchAuditLogs } from "@/lib/api";

export default async function LogsPage() {
  const logs = (await fetchAuditLogs())?.events || [];

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div>
        <p className="text-[11px] uppercase tracking-[0.2em] text-accent">Audit</p>
        <h1 className="mt-2 font-display text-3xl text-ink">Logs</h1>
        <p className="mt-2 text-sm text-ink-muted">Append-only audit trail under artifacts/audit.</p>
      </div>
      <section className="panel overflow-hidden">
        <div className="border-b border-canvas-border px-5 py-3">
          <SectionTitle title="Recent events" />
        </div>
        <div className="divide-y divide-canvas-border">
          {logs.map((e) => (
            <div key={String(e.id)} className="px-5 py-3">
              <p className="text-sm text-ink">{String(e.event)}</p>
              <p className="font-mono text-[10px] text-ink-faint">
                {String(e.ts)} · {String(e.actor)}
              </p>
            </div>
          ))}
          {!logs.length && <p className="px-5 py-6 text-sm text-ink-muted">No audit events yet.</p>}
        </div>
      </section>
    </div>
  );
}
