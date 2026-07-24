"use client";

import { motion } from "framer-motion";

export function MetricCard({
  label,
  value,
  hint,
  delay = 0,
}: {
  label: string;
  value: string | number;
  hint?: string;
  delay?: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay }}
      className="panel p-4"
    >
      <p className="text-[11px] uppercase tracking-[0.14em] text-ink-faint">{label}</p>
      <p className="mt-2 font-display text-3xl capitalize text-ink">{value}</p>
      {hint ? <p className="mt-1 text-xs text-ink-muted">{hint}</p> : null}
    </motion.div>
  );
}

export function SectionTitle({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <div className="mb-4">
      <h2 className="font-display text-xl text-ink">{title}</h2>
      {subtitle ? <p className="mt-1 text-sm text-ink-muted">{subtitle}</p> : null}
    </div>
  );
}
