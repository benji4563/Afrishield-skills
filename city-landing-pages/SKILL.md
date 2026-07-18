---
name: city-landing-pages
description: >
  Build SEO city/service landing pages from a keyword export file (Ahrefs, SEMrush, or CSV).
  Handles the full pipeline: read the keyword file → cluster by city → filter noise
  (competitor brands, recruiter/internship intent, thin volume) → generate city-specific
  components, data, and pages with local tax content, neighborhoods, FAQ, and JSON-LD.
  Uses Next.js App Router + Tailwind CSS + Framer Motion. Self-contained — works on fresh
  projects or existing sites. Use this skill whenever the user wants to create city landing
  pages, location pages, service-area pages, or local SEO pages from keyword data, even if
  they don't call them "city landing pages" explicitly.
---

# City Landing Pages — From Keywords to Live Pages

Turn a keyword export into a fleet of high-quality, SEO-optimised city/service landing pages. Each page mirrors the home page's structure but with city-specific H1, neighborhoods, local tax/compliance content, and FAQ — not thin template swaps.

## When to use this skill

- User provides a keyword file (.xlsx, .csv) with city/location keywords
- User asks for "city pages", "location pages", "service area pages", or "local landing pages"
- User wants to expand geographic SEO coverage from keyword research
- User says something like "build pages for these cities" or "create landing pages from this keyword data"

## Service-agnostic

The examples in this skill use accounting/tax services, but the pattern works for any local service business — law firms, dental offices, HVAC companies, marketing agencies, etc. Swap the service name and adjust the FAQ topics to match the industry's local compliance landscape.

## Stack assumptions

- **Next.js 14+ App Router** with TypeScript
- **Tailwind CSS** for styling
- **Framer Motion** for animations (optional — pages work without it)
- Pages live under `app/locations/[city-slug]/page.tsx`
- Components live under `components/locations/`

If the project doesn't have these yet, scaffold them. If it uses a different framework, adapt the patterns — the data architecture and content strategy are framework-agnostic.

---

## Phase 1 — Read and Understand the Keyword File

### Read the file

Keyword files come in two forms:
- **Excel (.xlsx)** — use COM automation (Windows) or a Python library to extract rows
- **CSV** — read directly

Expect columns like: `Keyword`, `Volume`, `KD` (keyword difficulty), `CPC`, `Intent`, `Seed keyword`, plus possibly `Competitive Density`, `SERP Features`, `Content references`, `Competitors`.

The exact column names vary by tool (Ahrefs, SEMrush, Ubersuggest). Identify which columns map to:
- **keyword** — the search query
- **volume** — monthly search volume
- **intent** — Commercial, Informational, Transactional, Navigational
- **CPC** — cost per click (signals commercial value)
- **seed keyword** — what the user originally searched in the tool (often contains the city name)

### Extract city signals

Cities appear in keywords in predictable patterns:
- `"accounting firms in [city]"`
- `"[city] accounting firms"`
- `"[service] [city] [state]"`
- `"[service] in [city] [state abbreviation]"`

Also check the `Seed keyword` column — it often contains `"accounting [City]"` or `"[service] [City]"` which directly tells you the city grouping.

---

## Phase 2 — Cluster and Filter

### Cluster by city

Group all keywords that reference the same city. Multiple keyword variants targeting the same city should be consolidated into one cluster:

```
Cincinnati cluster:
  "cincinnati accounting firms"     → 140/mo
  "accounting firms cincinnati"     → 70/mo
  "accounting firm cincinnati"      → 30/mo
  Combined volume: 240/mo
```

### Filter noise

Not every keyword in the file is relevant. Common noise categories:

| Noise type | Example | Why it's noise |
|---|---|---|
| Competitor brand | "lakeshore accounting" | Searching for a specific company, not a service |
| Recruiter intent | "accounting recruiters dallas" | Looking for staffing, not accounting services |
| Internship/career | "accounting internships dallas" | Job seekers, not clients |
| Education | "accounting degree programs chicago" | Students, not business owners |
| Too thin | 40/mo on a niche sub-service in a small city | Not worth a dedicated page |

**Decision rules:**
- **Skip** keywords where the dominant intent is navigational (searching for a specific brand)
- **Skip** keywords with recruiter, internship, job, career, degree, or salary modifiers — unless the business actually offers those services
- **Skip** city clusters under ~100/mo combined volume unless the business has a strong local presence there
- **Keep** commercial-intent keywords where someone is looking for the service the business offers

Present the clustering results to the user as a table before building pages:

```
| City | Combined Vol/mo | Primary Keyword | Action |
|---|---|---|---|
| San Diego | 730 | accounting firms in san diego | BUILD |
| Chicago | 550 | accounting firms chicago | BUILD |
| "Lakeshore" | 470 | lakeshore accounting | SKIP — competitor brand |
| Dallas (recruiters) | 620 | accounting recruiters dallas | SKIP — recruiter intent |
```

The user confirms which cities to build before proceeding.

### Pick the primary keyword per city

For each city, pick the keyword variant with the highest volume as the primary. This becomes the page's core target. All other variants in the cluster are secondary keywords that the page will naturally capture.

---

## Phase 3 — Create the Component System

Build three reusable, parameterized components. These accept props so every new city is just data — no new component files.

### CityHero

A hero section that mirrors the home page hero but with a city-specific H1.

**Props:**
- `cityName: string` — displayed in the H1
- `description: string` — the paragraph below the H1, mentioning local neighborhoods
- `floatingHeadline: string` — e.g., "Serving Dallas & the DFW Metroplex"
- `floatingSubline: string` — e.g., "Local expertise, remote-friendly delivery."

**H1 pattern:** `"A small-business [service] in [City]."` — where [service] matches the business's core offering.

The hero should include:
- The business's portrait/photo (reuse from home page)
- CTAs (Book a call + See pricing)
- A floating proof badge

See `references/component-templates.md` for the full implementation.

### CityLocalTrust

A "Where we work" section that establishes local credibility.

**Props:**
- `heading: string` — e.g., "Serving Dallas and the DFW metroplex."
- `paragraphs: string[]` — 2 paragraphs: first about remote delivery + local knowledge, second about coverage area
- `neighborhoods: string[]` — 10-12 named neighborhoods/suburbs

The first paragraph should mention specific local compliance details (state tax quirks, municipal filing requirements) to prove genuine local knowledge — not generic filler.

### CityFaq

A FAQ section with city-specific questions and answers.

**Props:**
- `eyebrow: string` — e.g., "Dallas-specific questions"
- `heading: string` — e.g., "Questions Dallas small-business owners ask us most."
- `items: Array<{ q: string; a: string }>` — 6 FAQ items

Every city page should include these FAQ patterns:
1. **"Is this a real page?"** — Transparent acknowledgment that yes, this is optimized for search, AND the business genuinely serves this area
2. **Local tax/compliance question** — The city or state's specific tax situation (franchise tax, municipal income tax, sales tax rate, etc.)
3. **State-specific regulation** — Something unique to the state (e.g., Ohio CAT, California franchise tax minimum, Texas margin tax)
4. **Sales tax + nexus** — How local sales tax works and online seller obligations
5. **Credentials question** — CPA vs. accountant, what the client actually needs
6. **"Do you have a local office?"** — Honest "no" with explanation of why that keeps costs low

---

## Phase 4 — Write City Data

Create a single data file (`lib/city-data.ts` or similar) that exports a typed config for each city.

**The CityConfig type:**

```typescript
export type CityConfig = {
  slug: string;           // URL slug: "san-diego", "chicago"
  name: string;           // Display name: "San Diego", "Chicago"
  state: string;          // Full state: "California", "Illinois"
  stateCode: string;      // Abbreviation: "CA", "IL"
  county: string;         // Primary county: "San Diego County"
  metaTitle: string;      // SEO title tag
  metaDescription: string; // SEO meta description
  heroDescription: string; // Hero paragraph
  floatingBadge: { headline: string; subline: string };
  neighborhoods: string[];  // 10-12 real neighborhoods
  localTrustHeading: string;
  localTrustBody: string[];  // 2 paragraphs
  localTrustRadius: string;
  faqEyebrow: string;
  faqHeading: string;
  faqs: Array<{ q: string; a: string }>;
};
```

**Content quality rules for city data:**

- **Neighborhoods must be real.** Use actual, well-known neighborhoods and suburbs — not ZIP codes or abstract "greater metro area." A local resident should recognize every name on the list.
- **Tax content must be accurate.** Each state has specific tax rules. Research and include the right ones:
  - Texas: no state income tax, but franchise/margin tax
  - California: $800 minimum franchise tax for LLCs
  - Ohio: municipal income tax in every city, CAT (Commercial Activity Tax)
  - Illinois: flat income tax, PTE tax election
  - North Carolina: flat income tax, privilege license
  - etc.
- **Don't fake local presence.** If the business is remote-first, say so honestly. The FAQ pattern "Do you have a [City] office?" → "No, and here's why that's better for you" builds more trust than pretending.

---

## Phase 5 — Create Page Files

Each city gets one page file at `app/locations/[slug]/page.tsx`.

**Page structure** (mirrors home page):

```
CityHero → ProofStrip → CityLocalTrust → EmotionalRecognition → ServicesGrid →
MeetNjock → FirstThirtyDays → CityFaq → PricingPreview → CtaDrop
```

City-specific components (Hero, LocalTrust, FAQ) get their data from the city config. Shared components (ProofStrip, EmotionalRecognition, ServicesGrid, etc.) are imported from the home page — they're identical across all city pages.

**If the project is fresh** and doesn't have home page components yet, the city page structure simplifies to:

```
CityHero → CityLocalTrust → CityFaq
```

Add the shared sections as the site grows.

### SEO metadata per page

**Meta title formula:** `[Service] in [City] [State Code] — [Core Offering] | [Brand]`
Example: `Small-Business Accountant in Dallas TX — Bookkeeping & Tax Services`

**Meta description formula:** `[Core pitch] for [City] small businesses. [Differentiator]. [Guarantee]. Serving [County/Region].`
Keep under 160 characters.

Every city page needs:

```typescript
export const metadata: Metadata = {
  title: c.metaTitle,
  description: c.metaDescription,
  alternates: { canonical: `/locations/${c.slug}` },
  openGraph: {
    title: c.metaTitle,
    description: c.metaDescription,
    url: `https://${DOMAIN}/locations/${c.slug}`,
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: c.metaTitle,
    description: c.metaDescription,
  },
};
```

### JSON-LD structured data per page

Three schemas per city page:
1. **LocalBusiness** — city-specific business listing
2. **FAQPage** — the city FAQ items
3. **BreadcrumbList** — Home → Locations → [City]

Use helper functions (like `localBusinessJsonLd()`, `faqPageJsonLd()`, `breadcrumbJsonLd()`) to generate these from the city config. If these helpers don't exist yet, create them in `lib/structured-data.ts`.

---

## Phase 6 — Update Sitemap and Keyword Tracker

### Sitemap

Add every new city page to the sitemap route (`app/sitemap.xml/route.ts` or `app/sitemap.ts`):

```typescript
{ path: '/locations/san-diego', priority: '0.8', changefreq: 'monthly' },
{ path: '/locations/chicago', priority: '0.8', changefreq: 'monthly' },
// ... etc
```

### Used keywords tracker

If the project has a used-keywords tracker (like `Keywords for accountant/used-keywords.md`), log each city's primary keyword:

```
| 2026-07-17 | accounting firms in san diego | /locations/san-diego | City landing page — San Diego, CA (730/mo) |
```

---

## Phase 7 — Verify

1. Start the dev server
2. Visit each city page — confirm:
   - Correct H1 with city name
   - Neighborhoods render
   - FAQ renders with city-specific content
   - No console errors
   - Page title includes city name
3. Spot-check that existing pages (home, other cities) still work
4. Run `tsc --noEmit` to confirm zero TypeScript errors

---

## Anti-patterns

| Don't | Do instead |
|---|---|
| Copy-paste a component file per city | Use one parameterized component + city data |
| Write generic "we serve [City]" filler | Include real local tax rules, real neighborhoods |
| Create pages for competitor brand keywords | Skip them — explain to user why |
| Build pages for <100/mo combined volume | Skip unless there's a strategic reason |
| Hardcode the domain in every file | Use a constant (`SITE_URL`) from structured-data helpers |
| Skip JSON-LD | Every city page needs LocalBusiness + FAQPage + BreadcrumbList |

## File inventory (what gets created)

```
lib/city-data.ts                          — all city configs
components/locations/CityHero.tsx         — parameterized hero
components/locations/CityLocalTrust.tsx   — parameterized local trust section
components/locations/CityFaq.tsx          — parameterized FAQ section
app/locations/[slug]/page.tsx             — one per city (6 files for 6 cities)
```

**Modified:**
```
app/sitemap.xml/route.ts                  — new routes added
Keywords/used-keywords.md                 — new primaries logged
```

## Relationship to other skills

This skill pairs with **ai-seo-website-builder** — use that skill to build the full site from scratch, then use this skill to expand geographic coverage with city pages after the site is live and keywords are researched.

## Exemplar

The reference implementation is **njaccountstax.com** — 7 city pages (Cincinnati hand-built, 6 others from this skill's workflow). The commit history at `github.com/benji4563/nj-accounting-and-tax-services` is the authoritative reference for how these files look when applied end-to-end.
