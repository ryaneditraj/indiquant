const faq = [
  {
    question: "What is Indiquant?",
    answer:
      "Indiquant is an open-source AI quant research operating system for Indian equity markets (NSE and BSE). You write a hypothesis, backtest it, walk-forward validate it, and keep an experiment ID for the result.",
  },
  {
    question: "Is Indiquant a trading bot?",
    answer:
      "Indiquant is a research lab. It does not place live orders with a broker. A paper broker plugin exists for simulated fills.",
  },
  {
    question: "Can I backtest NSE and BSE ideas without a broker API key?",
    answer:
      "Yes. The default data provider is an offline fixture, and sample CSV files ship in data/sample_csv. Live NSE or BSE HTTP adapters stay quiet until DATA_NSE_API_BASE_URL or DATA_BSE_API_BASE_URL is set.",
  },
  {
    question: "What does the Google Trends search-demand score measure?",
    answer:
      "It is a relative 0–100 search index for configured brand, transactional, category, competitor, and risk queries in India. It is not absolute search volume and it is not a promise of returns.",
  },
  {
    question: "How does walk-forward validation work in Indiquant?",
    answer:
      "The validation suite replays a strategy across rolling train and test windows, then adds out-of-sample, Monte Carlo, and lookahead or leakage checks. A strategy is easier to reject when those checks fail.",
  },
  {
    question: "Can I use Indiquant in a commercial product?",
    answer:
      "Personal research, education, and noncommercial organizations can use it under the PolyForm Noncommercial License 1.0.0. A paid product, SaaS, or commercial trading desk needs a separate license from Money Radar / Thugir Group.",
  },
  {
    question: "Who maintains Indiquant?",
    answer:
      "Ryan Editraj maintains the GitHub repository. Indiquant is a Money Radar product built by Thugir Group.",
  },
  {
    question: "How do I report a security vulnerability in Indiquant?",
    answer:
      "Open a private GitHub security advisory on ryaneditraj/indiquant. Do not file a public issue for a vulnerability. See SECURITY.md.",
  },
];

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
        "@type": "Person",
        "@id": "https://github.com/ryaneditraj/#person",
        name: "Ryan Editraj",
        url: "https://github.com/ryaneditraj",
        sameAs: [
          "https://github.com/ryaneditraj",
          "https://instagram.com/ryaneditraj",
        ],
        jobTitle: "AI builder",
      },
      {
        "@type": "SoftwareApplication",
        name: "Indiquant",
        applicationCategory: "FinanceApplication",
        operatingSystem: "Web, macOS, Linux, Windows",
        url: "https://moneyradar.in/indiquant",
        codeRepository: "https://github.com/ryaneditraj/indiquant",
        description:
          "Open-source AI quant research OS for Indian equity markets (NSE and BSE): walk-forward backtesting, hypothesis-first research, and Google Trends search-demand scores.",
        offers: {
          "@type": "Offer",
          price: "0",
          priceCurrency: "INR",
          description: "Noncommercial open source under PolyForm Noncommercial 1.0.0",
        },
        author: [
          { "@id": "https://github.com/ryaneditraj/#person" },
          { "@id": "https://moneyradar.in/#organization" },
        ],
        publisher: { "@id": "https://moneyradar.in/#organization" },
        keywords:
          "NSE, BSE, quant research, walk-forward backtesting, Google Trends, Indian stock market, Money Radar, Indiquant",
      },
      {
        "@type": "WebSite",
        name: "Indiquant by Money Radar",
        url: "https://moneyradar.in/indiquant",
        publisher: { "@id": "https://moneyradar.in/#organization" },
      },
      {
        "@type": "FAQPage",
        mainEntity: faq.map((item) => ({
          "@type": "Question",
          name: item.question,
          acceptedAnswer: { "@type": "Answer", text: item.answer },
        })),
      },
    ],
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{
        __html: JSON.stringify(data).replace(/</g, "\\u003c"),
      }}
    />
  );
}
