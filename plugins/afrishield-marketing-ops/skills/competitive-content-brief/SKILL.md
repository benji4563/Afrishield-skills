---
name: competitive-content-brief
description: "Competitor content audit and gap analysis using Firecrawl scraping and SERP analysis. Scores content gaps, generates prioritized recommendations with effort/impact scoring, and outputs an actionable brief."
---

# Competitive Content Brief

Audit competitor content, analyze SERP positioning for cybersecurity terms in African markets, score content gaps, and generate a prioritized content plan for AfriShield.

---

## Step 1: Define Competitor Landscape

### 1A. Primary Competitors

Identify and categorize AfriShield's competitive set:

| Tier | Competitors | Market |
|------|-------------|--------|
| **Direct** (African cybersecurity) | Callsign Africa, Smile Identity, Seamfix, Prembly (formerly IdentityPass), Youverify, ThinkIT Africa | Pan-African |
| **Regional** (Market-specific) | CyberSOC Africa (Nigeria), Serianu (Kenya), Cyanre (South Africa), Surfshark Africa campaigns | Country-specific |
| **Global with Africa presence** | Kaspersky Africa, Sophos Africa, Palo Alto Networks Africa, Check Point Africa | Global-local |
| **Adjacent** (Fraud/fintech) | Flutterwave security, Paystack fraud tools, Interswitch security, MFS Africa | Fintech overlap |

### 1B. Target Keywords

Define the keyword universe across AfriShield's 4 revenue lines:

**Consumer cybersecurity:**
- cybersecurity africa, online security africa, fraud protection africa, phishing protection africa, mobile security africa, antivirus africa, identity theft protection africa, safe browsing africa, data privacy africa, cyber insurance africa

**B2B fraud detection:**
- fraud detection africa, enterprise cybersecurity africa, KYC solutions africa, AML compliance africa, identity verification africa, transaction monitoring africa, fraud prevention fintech africa, cybersecurity consulting africa, SOC as a service africa, penetration testing africa

**AI SEO:**
- AI SEO services africa, SEO agency africa, digital marketing cybersecurity, content marketing africa, search engine optimization africa, technical SEO africa, local SEO africa, enterprise SEO africa

**EA Services:**
- virtual assistant africa, executive assistant services, managed services africa, business process outsourcing africa

---

## Step 2: Scrape Competitor Content

### 2A. Crawl Competitor Websites

For each competitor in the direct and regional tiers, crawl their website to map content:

```tool
firecrawl_crawl({
  url: "<competitor_url>",
  maxDepth: 3,
  limit: 100,
  includePaths: ["/blog/*", "/resources/*", "/insights/*", "/news/*", "/case-studies/*", "/whitepapers/*", "/guides/*", "/webinars/*"],
  excludePaths: ["/careers/*", "/about/*", "/contact/*", "/legal/*", "/privacy/*"]
})
```

Check crawl status and retrieve results:

```tool
firecrawl_check_crawl_status({ id: "<crawl_id>" })
```

### 2B. Scrape Key Landing Pages

For each competitor, scrape their primary service pages to understand positioning:

```tool
firecrawl_scrape({
  url: "<competitor_service_page_url>",
  formats: ["markdown"],
  onlyMainContent: true
})
```

Target pages to scrape per competitor:
- Homepage (positioning and messaging)
- Main product/service pages (feature comparison)
- Pricing page (if public)
- Blog index (content volume and frequency)
- Resource/downloads page (gated content strategy)

### 2C. Extract Structured Data from Competitor Content

For each competitor's blog, extract structured content metadata:

```tool
firecrawl_extract({
  urls: ["<competitor_blog_url>/*"],
  prompt: "Extract all blog posts with: title, publication date, author, primary topic category (one of: fraud detection, cybersecurity, compliance, fintech security, data privacy, AI/ML security, mobile security, identity verification, market insights, product updates), target audience (consumer or B2B), estimated word count, whether it contains original research or data, whether it has downloadable assets (PDF, whitepaper, checklist)",
  schema: {
    type: "object",
    properties: {
      posts: {
        type: "array",
        items: {
          type: "object",
          properties: {
            title: { type: "string" },
            date: { type: "string" },
            author: { type: "string" },
            topic_category: { type: "string" },
            target_audience: { type: "string" },
            word_count: { type: "number" },
            has_original_research: { type: "boolean" },
            has_downloadable_asset: { type: "boolean" }
          }
        }
      }
    }
  }
})
```

---

## Step 3: Analyze SERP Positioning

### 3A. Search for Each Target Keyword

For every keyword in the target keyword list, perform a localized search:

```tool
firecrawl_search({
  query: "<keyword>",
  limit: 10,
  lang: "en",
  country: "ng",
  sourceType: "web"
})
```

Repeat for each primary African market:
- `country: "ng"` (Nigeria)
- `country: "ke"` (Kenya)
- `country: "za"` (South Africa)
- `country: "gh"` (Ghana)
- `country: "eg"` (Egypt)

After each search, submit feedback:

```tool
firecrawl_search_feedback({
  searchId: "<search_id>",
  searchQuery: "<keyword>",
  resultRanking: "good"
})
```

### 3B. Build SERP Position Matrix

For each keyword and market, record:

| Field | Description |
|-------|-------------|
| Keyword | The search term |
| Market | Country code |
| AfriShield position | Rank 1-10 or "not ranked" |
| Top 3 domains | Which competitors hold positions 1-3 |
| SERP features | Featured snippets, People Also Ask, video results present |
| Content type ranking | Blog post, landing page, tool, directory listing |
| Estimated monthly search volume | Low/Medium/High based on result diversity |

### 3C. Identify SERP Opportunities

Flag keywords where:
- AfriShield is not in the top 10 but a direct competitor is
- No African-focused content ranks in the top 5 (opportunity for localized content)
- Featured snippet is held by a weak or irrelevant domain
- People Also Ask questions have no Africa-specific answers
- The top results are outdated (published more than 18 months ago)

---

## Step 4: Score Content Gaps

### 4A. Topic Coverage Matrix

Build a matrix comparing AfriShield's content against competitors:

| Topic | AfriShield | Competitor A | Competitor B | Competitor C | Gap Score |
|-------|------------|-------------|-------------|-------------|-----------|
| (each topic from keyword categories) | Has/Missing | Has/Missing | Has/Missing | Has/Missing | 0-100 |

**Gap Score formula:**

```
Gap Score = (Competitor Coverage Score * 0.4) + (Search Demand Score * 0.3) + (Strategic Alignment Score * 0.3)

Where:
- Competitor Coverage Score = (Number of competitors covering topic / Total direct competitors) * 100
- Search Demand Score = Based on SERP analysis (High=100, Medium=60, Low=30)
- Strategic Alignment Score = How closely topic maps to AfriShield revenue lines (Direct=100, Adjacent=60, Tangential=30)
```

### 4B. Content Quality Gap Analysis

For topics where AfriShield has existing content, compare quality:

| Dimension | Scoring Criteria |
|-----------|-----------------|
| **Depth** | Word count relative to top-ranking competitor content. Score: competitor avg / AfriShield count (capped at 100) |
| **Freshness** | Days since last update. Score: 100 if updated within 90 days, -10 per additional 30 days |
| **Original research** | Does AfriShield content include proprietary data, surveys, or case studies? +30 if yes |
| **Visual assets** | Charts, infographics, diagrams present? +20 if yes |
| **Downloadable resources** | Gated PDF, checklist, template? +20 if yes |
| **Africa-specific data** | References African markets, regulations, companies, statistics? +30 if yes |

**Quality Gap = Competitor quality score - AfriShield quality score**

### 4C. Content Format Gap Analysis

Identify content formats competitors use that AfriShield does not:

| Format | Check |
|--------|-------|
| Long-form guides (3000+ words) | Present on competitor sites? |
| Interactive tools/calculators | e.g., "Is your business at risk?" assessment |
| Video content | YouTube, embedded tutorials |
| Podcast/audio | Interview series, market commentary |
| Webinar recordings | On-demand educational content |
| Case studies with named clients | Social proof with African businesses |
| Regulatory guides by country | Nigeria NDPR, Kenya DPA, SA POPIA compliance guides |
| Comparison pages | "AfriShield vs. [Competitor]" or category comparisons |
| Glossaries/educational hubs | Cybersecurity terminology for African audiences |
| Templates and checklists | Downloadable practical resources |

---

## Step 5: Generate Prioritized Recommendations

### 5A. Effort/Impact Scoring

Score each content recommendation on two axes:

**Impact Score (1-10):**

| Factor | Weight | Scoring |
|--------|--------|---------|
| Gap Score from 4A | 0.25 | Scaled 1-10 from raw gap score |
| SERP opportunity from 3C | 0.25 | 10 if no strong competitor ranks, 5 if weak competition, 2 if strong competition |
| Revenue line alignment | 0.20 | 10 for B2B Cyber (highest margin), 8 for AI SEO, 6 for Consumer, 4 for EA Services |
| Lead generation potential | 0.15 | 10 if topic maps to high-intent keyword, 5 for informational, 2 for navigational |
| Brand authority building | 0.15 | 10 if establishes thought leadership in African cybersec, 5 if general value, 2 if commodity content |

**Effort Score (1-10):**

| Factor | Weight | Scoring |
|--------|--------|---------|
| Content length required | 0.25 | 2 for <1000 words, 5 for 1000-3000, 8 for 3000+, 10 for pillar content |
| Research depth needed | 0.25 | 2 for opinion/commentary, 5 for secondary research, 8 for primary research, 10 for original data collection |
| Subject matter expertise | 0.20 | 2 for general marketing, 5 for cybersec knowledge, 8 for deep technical, 10 for requires external expert |
| Asset creation | 0.15 | 2 for text only, 5 for basic graphics, 8 for interactive/video, 10 for tool development |
| Localization requirement | 0.15 | 2 for English only, 5 for multi-market, 8 for multi-language, 10 for country-specific legal review needed |

**Priority Score = Impact Score / Effort Score** (higher is better)

### 5B. Recommendation Categories

Sort all recommendations into priority tiers:

**Tier 1 -- Quick Wins (Priority Score > 1.5):**
High impact, low effort. Execute within 1-2 weeks.

**Tier 2 -- Strategic Investments (Impact > 7, regardless of effort):**
High impact even if high effort. Plan for 2-6 week execution.

**Tier 3 -- Fill-ins (Priority Score 0.8-1.5):**
Moderate impact and effort. Schedule as bandwidth allows.

**Tier 4 -- Backlog (Priority Score < 0.8):**
Low priority. Revisit quarterly.

---

## Step 6: Output the Brief

### 6A. Brief Header

Render a branded header with show_widget:
- Title in Sora: "Competitive Content Brief"
- Subtitle in Inter: Generation date and analysis period
- Brand colors: primary `#0F7248`, dark `#073F27`, light `#EAF7F1`

### 6B. Executive Summary

A 3-5 sentence summary covering:
- Number of competitors analyzed and content pieces reviewed
- Top 3 biggest content gaps identified
- Estimated organic traffic opportunity if gaps are filled
- Single most urgent recommendation

### 6C. SERP Position Heatmap

Render with show_widget a heatmap table:
- Rows: Target keywords (grouped by revenue line)
- Columns: African markets (NG, KE, ZA, GH, EG)
- Cell color: Green (`#0F7248`) if AfriShield ranks top 5, amber if ranks 6-10, red if not ranked
- Cell text: Current rank position or "--"

### 6D. Content Gap Scorecard

Render with show_widget a sorted table:
- Columns: Topic, Gap Score, AfriShield Status, Top Competitor, SERP Opportunity, Recommended Action
- Sorted by Gap Score descending
- Top 5 rows highlighted with brand green background
- Conditional formatting on Gap Score: >70 red, 40-70 amber, <40 green

### 6E. Prioritized Recommendations Table

Render with show_widget:
- Columns: Rank, Topic/Title, Content Type, Target Keywords, Target Revenue Line, Impact Score, Effort Score, Priority Score, Recommended Publish Date
- Grouped by tier (Quick Wins, Strategic, Fill-ins, Backlog)
- Each tier has a header row with tier description
- Color-coded Priority Score column

### 6F. Detailed Recommendation Cards

For the top 10 recommendations, output a detailed card for each:

| Field | Content |
|-------|---------|
| **Title** | Proposed content title |
| **Content type** | Blog post, guide, whitepaper, landing page, video script, tool, etc. |
| **Target keywords** | Primary keyword + 3-5 secondary keywords |
| **Target markets** | Which African markets this content targets |
| **Revenue line** | Which AfriShield revenue line this supports |
| **Competitor benchmark** | Link to the best competing content piece on this topic |
| **Differentiation angle** | What makes AfriShield's take unique (Africa focus, proprietary data, specific expertise) |
| **Outline** | 5-8 bullet point content outline |
| **Required assets** | Graphics, data, expert quotes, screenshots needed |
| **Distribution plan** | Organic, email, social, partner channels for this piece |
| **Success metrics** | Target ranking position, traffic, leads, conversion |
| **Estimated effort** | Hours and roles needed (writer, designer, SME reviewer) |

### 6G. Competitive Content Calendar

Render with show_widget a 12-week content calendar:
- Rows: Weeks 1-12
- Columns: Content piece, Type, Target keyword, Revenue line, Status
- Tier 1 items scheduled in weeks 1-4
- Tier 2 items scheduled in weeks 3-8
- Tier 3 items distributed across weeks 5-12
- Brand-colored status indicators: Planned (light green), In Progress (primary green), Published (dark green)
