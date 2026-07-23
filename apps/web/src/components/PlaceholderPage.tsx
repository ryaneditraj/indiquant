import { SectionTitle } from "@/components/ui";

export default function PlaceholderPage({
  title,
  blurb,
}: {
  title: string;
  blurb: string;
}) {
  return (
    <div className="mx-auto max-w-3xl">
      <p className="text-[11px] uppercase tracking-[0.2em] text-accent">Coming online</p>
      <h1 className="mt-2 font-display text-3xl text-ink">{title}</h1>
      <p className="mt-3 text-sm text-ink-muted">{blurb}</p>
      <div className="panel mt-8 p-5">
        <SectionTitle
          title="Phase gate"
          subtitle="Tracked in ROADMAP.md — implement only when it helps discover a real edge."
        />
        <p className="text-sm text-ink-muted">
          This route is wired in navigation so the research OS shell stays complete while subsystems
          land behind config flags and tests.
        </p>
      </div>
    </div>
  );
}
