import Link from "next/link";

import { SectionTitle } from "@/components/ui";

export default function DocsPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <p className="text-[11px] uppercase tracking-[0.2em] text-accent">Documentation</p>
        <h1 className="mt-2 font-display text-3xl text-ink">Pramana docs</h1>
        <p className="mt-2 text-sm text-ink-muted">
          Pramana means <em>means of valid knowledge</em>. This OS privileges evidence over
          intuition.
        </p>
      </div>

      <section className="panel p-5 space-y-3">
        <SectionTitle title="In-repo guides" />
        <ul className="space-y-2 text-sm text-ink-muted">
          <li>
            <span className="text-ink">README.md</span> — quick start & philosophy
          </li>
          <li>
            <span className="text-ink">docs/architecture.md</span> — system design
          </li>
          <li>
            <span className="text-ink">docs/brand.md</span> — name, voice, visual system
          </li>
          <li>
            <span className="text-ink">ROADMAP.md</span> — what ships next
          </li>
          <li>
            <span className="text-ink">CONTRIBUTING.md</span> — how to help
          </li>
        </ul>
      </section>

      <section className="panel p-5 space-y-3">
        <SectionTitle title="Try the loop" />
        <p className="text-sm text-ink-muted">
          Open <Link href="/ai-lab" className="text-accent">AI Lab</Link> and start a short forever
          loop, or run a single cycle from{" "}
          <Link href="/research" className="text-accent">Research</Link>.
        </p>
      </section>
    </div>
  );
}
