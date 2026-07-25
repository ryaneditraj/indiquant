export function JsonLd() {
  const data = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Organization",
        "@id": "https://moneyradar.in/#organization",
        name: "Money Radar",
        url: "https://moneyradar.in",
        parentOrganization: {
          "@type": "Organization",
          name: "Thugir Group",
        },
        sameAs: ["https://moneyradar.in"],
      },
      {
        "@type": "SoftwareApplication",
        name: "Indiquant",
        applicationCategory: "FinanceApplication",
        operatingSystem: "Web, macOS, Linux, Windows",
        url: "https://moneyradar.in/indiquant",
        codeRepository: "https://github.com/ryaneditraj/indiquant",
        description:
          "Open-source AI quantitative research OS for Indian equity markets (NSE/BSE). Evidence-first — not a trading bot.",
        offers: {
          "@type": "Offer",
          price: "0",
          priceCurrency: "INR",
          description: "Non-commercial open source under PolyForm Noncommercial 1.0.0",
        },
        author: { "@id": "https://moneyradar.in/#organization" },
        publisher: { "@id": "https://moneyradar.in/#organization" },
        keywords:
          "NSE, BSE, quant research, AI agents, backtesting, Indian stock market, Money Radar, Thugir Group",
      },
      {
        "@type": "WebSite",
        name: "Indiquant by Money Radar",
        url: "https://moneyradar.in/indiquant",
        publisher: { "@id": "https://moneyradar.in/#organization" },
      },
    ],
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  );
}
