import type { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = process.env.NEXT_PUBLIC_SITE_URL || "https://moneyradar.in/indiquant";
  const paths = [
    "",
    "/research",
    "/experiments",
    "/strategies",
    "/datasets",
    "/backtests",
    "/validation",
    "/portfolio",
    "/ai-lab",
    "/notebook",
    "/settings",
    "/docs",
  ];
  return paths.map((path) => ({
    url: `${base}${path}`,
    lastModified: new Date(),
    changeFrequency: "weekly" as const,
    priority: path === "" ? 1 : 0.7,
  }));
}
