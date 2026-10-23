import type { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = process.env.NEXT_PUBLIC_SITE_URL || "https://moneyradar.in/indiquant";
  const paths = [
    "",
    "/research",
    "/experiments",
    "/strategies",
    "/datasets",
    "/trends",
    "/backtests",
    "/validation",
    "/portfolio",
    "/optimization",
    "/ai-lab",
    "/notebook",
    "/logs",
    "/settings",
    "/docs",
  ];
  const lastModified = new Date("2026-10-23");
  return paths.map((path) => ({
    url: `${base}${path}`,
    lastModified,
    changeFrequency: "weekly" as const,
    priority: path === "" ? 1 : 0.7,
  }));
}
