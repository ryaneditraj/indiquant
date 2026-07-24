import type { Metadata } from "next";
import { Fraunces, IBM_Plex_Mono, Sora } from "next/font/google";

import { AppShell } from "@/components/AppShell";

import "./globals.css";

const display = Fraunces({
  subsets: ["latin"],
  variable: "--font-display",
  weight: ["400", "500", "600", "700"],
});

const sans = Sora({
  subsets: ["latin"],
  variable: "--font-sans",
  weight: ["400", "500", "600"],
});

const mono = IBM_Plex_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  weight: ["400", "500"],
});

const appName = process.env.NEXT_PUBLIC_APP_NAME || "Pramana";

export const metadata: Metadata = {
  title: {
    default: `${appName} — Evidence-first quant research OS`,
    template: `%s · ${appName}`,
  },
  description:
    "Open-source AI quantitative research operating system for Indian markets. Hypotheses first. Validation always.",
  icons: {
    icon: "/brand.svg",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${display.variable} ${sans.variable} ${mono.variable} font-sans`}>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
