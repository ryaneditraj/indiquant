import { SectionTitle } from "@/components/ui";
import { apiBase } from "@/lib/api";

async function examples() {
  try {
    const res = await fetch(`${apiBase()}/api/v1/notebook/examples`, { next: { revalidate: 60 } });
    if (!res.ok) return [];
    const json = await res.json();
    return json.notebooks || [];
  } catch {
    return [];
  }
}

export default async function NotebookPage() {
  const notebooks = await examples();

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <p className="text-[11px] uppercase tracking-[0.2em] text-accent">Notebooks</p>
        <h1 className="mt-2 font-display text-3xl text-ink">Notebook</h1>
        <p className="mt-2 text-sm text-ink-muted">
          Templates for reproducible research. Full in-browser kernel execution lands next.
        </p>
      </div>
      {notebooks.map((nb: Record<string, unknown>) => (
        <section key={String(nb.id)} className="panel p-5 space-y-3">
          <SectionTitle title={String(nb.title)} />
          <pre className="whitespace-pre-wrap text-sm text-ink-muted">{String(nb.markdown)}</pre>
          <pre className="overflow-auto rounded-lg bg-canvas p-3 font-mono text-xs text-accent">
            {String(nb.code)}
          </pre>
        </section>
      ))}
    </div>
  );
}
