---
name: data-scraper
description: "Firecrawl-powered web intelligence collector for AfriShield. Gathers competitive intel, market sizing data, and prospect enrichment from African cybersecurity, fintech, and enterprise markets using firecrawl_search, firecrawl_scrape, and firecrawl_extract."
---

# AfriShield Data Scraper

Systematic web intelligence collection for AfriShield's four revenue lines (Consumer, B2B Cyber, AI SEO, EA Services) across African markets. Uses Firecrawl tools exclusively for data collection.

---

## Tools Used

| Tool | Purpose |
|---|---|
| `firecrawl_search` | Broad web search with content extraction. Primary discovery tool. |
| `firecrawl_scrape` | Deep single-page scrape with full content. Used after search identifies targets. |
| `firecrawl_extract` | Structured data extraction from pages using schemas. Used for prospect enrichment and pricing extraction. |
| `firecrawl_search_feedback` | Submit feedback on search quality after each search. Improves results and refunds 1 credit. |

---

## Research Templates

### Template 1: Competitor Analysis

**Purpose:** Build a profile of a named competitor operating in African cybersecurity, fraud detection, or fintech markets.

**Step 1 -- Discovery Search**

```
firecrawl_search({
  query: "[COMPETITOR NAME] cybersecurity Africa",
  limit: 10,
  lang: "en",
  scrapeOptions: { formats: ["markdown"] }
})
```

Then search for pricing and product specifics:

```
firecrawl_search({
  query: "[COMPETITOR NAME] pricing plans enterprise",
  limit: 5,
  lang: "en"
})
```

And for recent news and funding:

```
firecrawl_search({
  query: "[COMPETITOR NAME] funding round OR acquisition OR partnership 2025 2026",
  limit: 5,
  sourceType: "news"
})
```

**Step 2 -- Deep Scrape of Key Pages**

For each relevant result URL from Step 1:

```
firecrawl_scrape({
  url: "[TARGET_URL]",
  formats: ["markdown"],
  onlyMainContent: true
})
```

Priority pages to scrape:
- Product/features page
- Pricing page
- About/team page
- Case studies or customer logos page
- Careers page (indicates growth areas and tech stack)

**Step 3 -- Structured Extraction**

```
firecrawl_extract({
  urls: ["[COMPETITOR_URL]/pricing", "[COMPETITOR_URL]/products"],
  prompt: "Extract the company's product names, pricing tiers, target customer segments, key features per tier, and any mentioned African market presence or partnerships.",
  schema: {
    type: "object",
    properties: {
      products: {
        type: "array",
        items: {
          type: "object",
          properties: {
            name: { type: "string" },
            description: { type: "string" },
            pricing: { type: "string" },
            target_segment: { type: "string" },
            key_features: { type: "array", items: { type: "string" } }
          }
        }
      },
      african_markets: { type: "array", items: { type: "string" } },
      partnerships: { type: "array", items: { type: "string" } },
      team_size_estimate: { type: "string" },
      funding_status: { type: "string" }
    }
  }
})
```

**Step 4 -- Feedback**

After each `firecrawl_search`, call:

```
firecrawl_search_feedback({
  searchId: "[SEARCH_ID_FROM_RESULT]",
  searchQuery: "[ORIGINAL_QUERY]",
  feedback: "positive"  // or "negative" with details
})
```

**Output Format:**

```markdown
## Competitor Profile: [NAME]

### Overview
- Founded: [year]
- HQ: [location]
- Funding: [status]
- Team size: [estimate]

### Products & Pricing
| Product | Segment | Price | Key Features |
|---|---|---|---|

### African Market Presence
- Countries: [list]
- Key clients: [list]
- Partnerships: [list]

### Strengths vs. AfriShield
- [bullet points]

### Weaknesses / Gaps
- [bullet points]

### Sources
- [numbered list of URLs with scrape dates]
```

---

### Template 2: Market Sizing

**Purpose:** Estimate the addressable market for a specific AfriShield revenue line in a target geography.

**Step 1 -- Macro Market Data**

```
firecrawl_search({
  query: "cybersecurity market size Africa 2025 2026 forecast billion",
  limit: 10,
  lang: "en"
})
```

```
firecrawl_search({
  query: "digital payments fraud Africa statistics 2025 2026",
  limit: 10,
  lang: "en"
})
```

```
firecrawl_search({
  query: "[TARGET COUNTRY] fintech companies total number registered",
  limit: 5,
  lang: "en"
})
```

**Step 2 -- Regulatory and Infrastructure Context**

```
firecrawl_search({
  query: "[TARGET COUNTRY] data protection law cybersecurity regulation",
  limit: 5
})
```

```
firecrawl_search({
  query: "[TARGET COUNTRY] internet penetration mobile money users statistics",
  limit: 5
})
```

**Step 3 -- Report Sources Deep Scrape**

For analyst reports and data sources found in Steps 1-2:

```
firecrawl_scrape({
  url: "[REPORT_URL]",
  formats: ["markdown"],
  onlyMainContent: true
})
```

**Output Format:**

```markdown
## Market Sizing: [Revenue Line] in [Geography]

### Total Addressable Market (TAM)
- Global reference: $[X]B ([source])
- Africa share: $[X]B ([source])
- [Country/region] share: $[X]M (derived)

### Serviceable Addressable Market (SAM)
- Target segment: [description]
- Estimated companies in segment: [number]
- Average contract value assumption: $[X]/yr
- SAM estimate: $[X]M

### Serviceable Obtainable Market (SOM)
- Realistic penetration in Year 1: [X]%
- SOM estimate: $[X]M
- Basis: [reasoning]

### Key Drivers
1. [driver with supporting data]
2. [driver with supporting data]
3. [driver with supporting data]

### Key Risks
1. [risk]
2. [risk]

### Data Sources
- [numbered list with URLs and access dates]
```

---

### Template 3: Prospect Research / Enrichment

**Purpose:** Build a detailed profile of a prospective client before outreach.

**Step 1 -- Company Discovery**

```
firecrawl_search({
  query: "[PROSPECT COMPANY] [COUNTRY] fintech OR bank OR payments",
  limit: 10,
  lang: "en"
})
```

```
firecrawl_search({
  query: "[PROSPECT COMPANY] CEO OR CTO OR CISO leadership team",
  limit: 5
})
```

**Step 2 -- Deep Scrape Company Site**

```
firecrawl_scrape({
  url: "[PROSPECT_WEBSITE]",
  formats: ["markdown"],
  onlyMainContent: true
})
```

```
firecrawl_scrape({
  url: "[PROSPECT_WEBSITE]/about",
  formats: ["markdown"],
  onlyMainContent: true
})
```

**Step 3 -- Structured Extraction**

```
firecrawl_extract({
  urls: ["[PROSPECT_WEBSITE]", "[PROSPECT_WEBSITE]/about", "[PROSPECT_WEBSITE]/products"],
  prompt: "Extract the company description, products/services offered, leadership team names and titles, number of employees if mentioned, countries of operation, and any mentioned technology stack or security certifications.",
  schema: {
    type: "object",
    properties: {
      company_name: { type: "string" },
      description: { type: "string" },
      products: { type: "array", items: { type: "string" } },
      leadership: {
        type: "array",
        items: {
          type: "object",
          properties: {
            name: { type: "string" },
            title: { type: "string" }
          }
        }
      },
      employee_count: { type: "string" },
      countries: { type: "array", items: { type: "string" } },
      tech_stack: { type: "array", items: { type: "string" } },
      certifications: { type: "array", items: { type: "string" } }
    }
  }
})
```

**Step 4 -- Pain Point and Trigger Search**

```
firecrawl_search({
  query: "[PROSPECT COMPANY] data breach OR fraud OR security incident",
  limit: 5,
  sourceType: "news"
})
```

```
firecrawl_search({
  query: "[PROSPECT COMPANY] expansion OR new market OR Series funding round",
  limit: 5,
  sourceType: "news"
})
```

**Output Format:**

```markdown
## Prospect Profile: [COMPANY NAME]

### Company Overview
- Industry: [sector]
- HQ: [city, country]
- Founded: [year]
- Employees: [estimate]
- Funding: [stage/amount]

### Products & Services
- [list]

### Leadership (Key Contacts)
| Name | Title | LinkedIn | Notes |
|---|---|---|---|

### African Footprint
- Operating in: [countries]
- Expanding to: [countries, if known]

### Potential Pain Points
- [pain point with evidence]

### Buying Triggers
- [recent event that creates urgency]

### AfriShield Fit
- Recommended revenue line: [Consumer / B2B Cyber / AI SEO / EA Services]
- Pitch angle: [one sentence]
- Estimated deal size: [range]

### Sources
- [numbered list]
```

---

## Known Competitor Watchlist (African Cybersecurity & Fintech Security)

Use these as starting points for competitive intelligence runs:

| Company | Focus | Geography |
|---|---|---|
| Callsign | Fraud / identity | Pan-Africa |
| Entersekt | Authentication | South Africa, expanding |
| Prembly (Identitypass) | KYC / identity verification | Nigeria, Pan-Africa |
| Smile Identity | Identity verification | Pan-Africa |
| CredoLab | Credit scoring / fraud | Emerging markets |
| Cybervergent | Managed security | Nigeria |
| Serianu | Cybersecurity consulting | East Africa |
| Digital Encode | Cybersecurity | West Africa |
| Liquid C2 (Cassava) | Cloud security | Pan-Africa |

---

## Search Query Patterns for African Markets

When searching for African market data, use these query modifiers to improve result quality:

- Add specific country names (Nigeria, Kenya, South Africa, Egypt, Ghana) rather than just "Africa"
- Include "Sub-Saharan" or "SSA" for regional aggregates
- Use both "cybersecurity" and "cyber security" (spelling varies by region)
- Include regulatory body names: CBN (Nigeria), SARB (South Africa), CBK (Kenya), CBE (Egypt)
- For market data, search for reports from: Frost & Sullivan, McKinsey Africa, Bain Africa, Partech Africa, Disrupt Africa

---

## Rate Limiting and Best Practices

1. **Always call `firecrawl_search_feedback`** after every search to improve quality and recover credits.
2. **Batch related searches** rather than running them one at a time. Plan the full research arc, then execute.
3. **Prefer `firecrawl_extract` with schemas** over manually parsing scraped markdown when you need structured data.
4. **Cache results mentally** -- if you already scraped a URL in this session, do not scrape it again.
5. **Respect robots.txt** -- Firecrawl handles this automatically, but if a scrape returns empty, note it and move on.
6. **Date-qualify searches** -- African markets move fast. Always include year qualifiers (2025, 2026) for market data.
