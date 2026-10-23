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
          product by Thugir Group — evidence-first quant research for NSE and BSE.
          Maintained by{" "}
          <a href="https://github.com/ryaneditraj" className="text-accent hover:underline">
            Ryan Editraj
          </a>
          .
        </p>
      </div>

      <section className="panel space-y-4 p-5">
        <SectionTitle title="FAQ" subtitle="Plain answers for researchers and answer engines" />
        <dl className="space-y-4 text-sm">
          <div>
            <dt className="text-ink">What is Indiquant?</dt>
            <dd className="mt-1 text-ink-muted">
              Indiquant is an open-source AI quant research operating system for Indian equity
              markets (NSE and BSE). You write a hypothesis, backtest it, walk-forward validate it,
              and keep an experiment ID for the result.
            </dd>
          </div>
          <div>
            <dt className="text-ink">Is Indiquant a trading bot?</dt>
            <dd className="mt-1 text-ink-muted">
              Indiquant is a research lab. It does not place live orders with a broker. A paper
              broker plugin exists for simulated fills.
            </dd>
          </div>
          <div>
            <dt className="text-ink">Can I backtest NSE and BSE ideas without a broker API key?</dt>
            <dd className="mt-1 text-ink-muted">
              Yes. The default data provider is an offline fixture, and sample CSV files ship in
              the repository. Live NSE or BSE HTTP adapters stay quiet until their base URLs are set.
            </dd>
          </div>
          <div>
            <dt className="text-ink">What does the Google Trends search-demand score measure?</dt>
            <dd className="mt-1 text-ink-muted">
              It is a relative 0–100 search index for configured brand, transactional, category,
              competitor, and risk queries in India. It is not absolute search volume and it is not
              a promise of returns.
            </dd>
          </div>
          <div>
            <dt className="text-ink">How does walk-forward validation work in Indiquant?</dt>
            <dd className="mt-1 text-ink-muted">
              The validation suite replays a strategy across rolling train and test windows, then
              adds out-of-sample, Monte Carlo, and lookahead or leakage checks. A strategy is easier
              to reject when those checks fail.
            </dd>
          </div>
          <div>
            <dt className="text-ink">Can I use Indiquant in a commercial product?</dt>
            <dd className="mt-1 text-ink-muted">
              Personal research, education, and noncommercial organizations can use it under the
              PolyForm Noncommercial License 1.0.0. A paid product, SaaS, or commercial trading desk
              needs a separate license from Money Radar / Thugir Group.
            </dd>
          </div>
          <div>
            <dt className="text-ink">Who maintains Indiquant?</dt>
            <dd className="mt-1 text-ink-muted">
              <a href="https://github.com/ryaneditraj" className="text-accent hover:underline">
                Ryan Editraj
              </a>{" "}
              maintains the GitHub repository. Indiquant is a Money Radar product built by Thugir
              Group.
            </dd>
          </div>
          <div>
            <dt className="text-ink">How do I report a security vulnerability in Indiquant?</dt>
            <dd className="mt-1 text-ink-muted">
              Open a private GitHub security advisory on ryaneditraj/indiquant. Do not file a public
              issue for a vulnerability. See SECURITY.md. Machine-readable overview:{" "}
              <a href="/llms.txt" className="text-accent hover:underline">
                llms.txt
              </a>
              .
            </dd>
          </div>
        </dl>
      </section>

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
