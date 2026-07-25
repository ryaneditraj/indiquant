"use client";

import type { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger";

const styles: Record<Variant, string> = {
  primary:
    "bg-accent text-canvas font-semibold shadow-[0_0_20px_rgba(61,255,154,0.2)] hover:brightness-110",
  secondary:
    "border border-canvas-border bg-canvas-elevated/80 text-ink hover:border-accent/40",
  ghost: "text-ink-muted hover:text-ink",
  danger: "border border-accent-bad/40 text-accent-bad hover:bg-accent-bad/10",
};

export function Button({
  variant = "primary",
  className = "",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  return (
    <button
      type="button"
      className={`inline-flex items-center justify-center rounded-xl px-3.5 py-2 text-sm transition disabled:cursor-not-allowed disabled:opacity-50 ${styles[variant]} ${className}`}
      {...props}
    />
  );
}
