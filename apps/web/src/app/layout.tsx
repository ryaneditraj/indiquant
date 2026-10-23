import type { Metadata, Viewport } from "next";
import { Fraunces, IBM_Plex_Mono, Sora } from "next/font/google";

import { AppShell } from "@/components/AppShell";
import { JsonLd } from "@/components/JsonLd";

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

const appName = process.env.NEXT_PUBLIC_APP_NAME || "Indiquant";
const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://moneyradar.in/indiquant";
const parentUrl = process.env.NEXT_PUBLIC_PARENT_URL || "https://moneyradar.in";

export const viewport: Viewport = {
  themeColor: "#030712",
  colorScheme: "dark",
};

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: `${appName} by Money Radar — AI Quant Research OS for Indian Markets (NSE/BSE)`,
    template: `%s · ${appName} · Money Radar`,
  },
  description:
    "Open-source AI quant research OS for Indian markets (NSE and BSE). Hypothesis-first strategy discovery, walk-forward backtesting, and Google Trends search-demand scores. Maintained by Ryan Editraj. A Money Radar product by Thugir Group.",
  applicationName: appName,
  authors: [
    { name: "Ryan Editraj", url: "https://github.com/ryaneditraj" },
    { name: "Thugir Group", url: parentUrl },
  ],
  creator: "Ryan Editraj",
  publisher: "Money Radar",
  keywords: [
    "Indiquant",
    "Money Radar",
    "Thugir Group",
    "Ryan Editraj",
    "Indian stock market research",
    "NSE",
    "BSE",
    "quant research OS",
    "walk-forward backtesting",
    "algorithmic trading research India",
    "Google Trends alternative data",
    "open source quant",
    "NSE BSE backtest",
  ],
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true, "max-image-preview": "large" },
  },
  alternates: {
    canonical: siteUrl,
  },
  openGraph: {
    type: "website",
    locale: "en_IN",
    url: siteUrl,
    siteName: "Indiquant",
    title: `${appName} — AI quant research OS for NSE and BSE`,
    description:
      "Hypothesis-first quant research for Indian markets. Walk-forward backtests and Google Trends search-demand scores. A Money Radar product by Thugir Group.",
    images: [
      {
        url: "/og.png",
        width: 1200,
        height: 630,
        alt: "Indiquant by Money Radar — AI Quant Research OS",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: `${appName} by Money Radar`,
    description:
      "Open-source AI quant research OS for Indian markets. Hypotheses first. Validation always.",
    images: ["/og.png"],
  },
  icons: {
    icon: "/brand.svg",
    apple: "/brand.svg",
  },
  category: "finance",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en-IN" className="dark">
      <body className={`${display.variable} ${sans.variable} ${mono.variable} font-sans`}>
        <JsonLd />
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
