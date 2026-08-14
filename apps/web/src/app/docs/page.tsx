import Link from "next/link";

import { SectionTitle } from "@/components/ui";

export default function DocsPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <p className="text-[11px] uppercase tracking-[0.2em] text-accent">Documentation</p>
        <h1 className="mt-2 font-display text-3xl text-ink">Indiquant docs</h1>
        <p className="mt-2 text-sm text-ink-muted">
          Indiquant is a{" "}
          <a href="https://moneyradar.in" className="text-accent-radar hover:underline">
            Money Radar
          </a>{" "}
          product by Thugir Group — evidence-first quant research for NSE/BSE.
        </p>
      </div>

      <section className="panel p-5 space-y-3">
        <SectionTitle title="Brand hierarchy" />
        <ul className="space-y-1 text-sm text-ink-muted">
          <li>
            <span className="text-ink">Thugir Group</span> — company
          </li>
          <li>
            <span className="text-ink">Money Radar</span> — parent platform (moneyradar.in)
          </li>
          <li>
            <span className="text-ink">Indiquant</span> — this research OS
          </li>
        </ul>
      </section>

      <section className="panel p-5 space-y-3">
        <SectionTitle title="License" />
        <p className="text-sm text-ink-muted">
          PolyForm Noncommercial 1.0.0 — free for research & education; commercial use requires a
          license from Money Radar / Thugir Group.
        </p>
      </section>

      <section className="panel p-5 space-y-3">
        <SectionTitle title="In-repo guides" />
        <ul className="space-y-2 text-sm text-ink-muted">
          <li>
            <span className="text-ink">README.md</span> — quick start
          </li>
          <li>
            <span className="text-ink">docs/brand.md</span> — brand system
          </li>
          <li>
            <span className="text-ink">docs/architecture.md</span> — design
          </li>
          <li>
            <span className="text-ink">docs/trends.md</span> — Google Trends intelligence (multi-entity + modeling)
          </li>
          <li>
            <span className="text-ink">ROADMAP.md</span> — what ships next
          </li>
          <li>
            <span className="text-ink">http://localhost:8000/docs</span> — interactive FastAPI (OpenAPI)
          </li>
        </ul>
      </section>

      <section className="panel p-5">
        <SectionTitle title="Try it" />
        <p className="text-sm text-ink-muted">
          Open <Link href="/trends" className="text-accent">Trends</Link>,{" "}
          <Link href="/ai-lab" className="text-accent">AI Lab</Link>, or{" "}
          <Link href="/research" className="text-accent">Research</Link>.
        </p>
      </section>
    </div>
  );
}
