import { SectionTitle } from "@/components/ui";

const GATES = [
  "Walk-forward",
  "Out of sample",
  "Monte Carlo",
  "Parameter sensitivity",
  "Lookahead / leakage heuristics",
  "Reproducibility score threshold",
];

export default function ValidationPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <p className="text-[11px] uppercase tracking-[0.2em] text-accent">Scientific gates</p>
        <h1 className="mt-2 font-display text-3xl text-ink">Validation</h1>
        <p className="mt-2 text-sm text-ink-muted">
          Every strategy must pass configured gates or it is rejected. Thresholds live in{" "}
          <code className="font-mono text-accent">config.yaml → validation</code>.
        </p>
      </div>
      <section className="panel p-5">
        <SectionTitle title="Active checks" />
        <ul className="space-y-2">
          {GATES.map((g) => (
            <li key={g} className="flex items-center gap-2 text-sm text-ink">
              <span className="h-1.5 w-1.5 rounded-full bg-accent-good" />
              {g}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
