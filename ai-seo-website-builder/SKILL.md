---
name: ai-seo-website-builder
description: End-to-end autonomous workflow for building a keyword-researched, SEO-optimised marketing website from scratch and deploying it to a live custom domain. Covers brand discovery, keyword clustering, Next.js scaffold with brand tokens, SEO foundation (metadata + JSON-LD + sitemap), a full blog-post pipeline (SERP research → image generation → publish), city landing pages, and Vercel deployment with nameserver-based custom domain. Triggers on any request like "build a website", "AI SEO site for [business]", "launch a marketing site", "new website for a client", or "SEO-optimised site from scratch." Argument is an optional one-line brief.
argument-hint: "<business name and one-line brief>"
user-invocable: true
---

# AI SEO Website Builder

You are executing an end-to-end website build. This skill codifies every step that produced `njaccountstax.com` — a live, deployed, SEO-optimised small-business marketing site with a research-backed pillar blog post, a city landing page, custom-domain HTTPS, and full schema.org markup.

The workflow is DELIBERATELY autonomous after Phase 0's discovery interview. Do not ask further clarifying questions unless something is materially ambiguous — every decision below has a documented default.

---

## Ground rules

1. **No code before specs exist.** Never write a `.tsx` file until `project_specs.md` and `brand-guidelines.md` are written and confirmed.
2. **All prose is original composition.** Extract structural patterns and topic maps from reference sources; never reproduce prose or sentences verbatim.
3. **Keyword filter: 70–80% of raw Ahrefs exports are noise.** State-gov queries, career searches, competitor brand names, gaming/social/login queries, adjacent product research — all skip clusters. Only target rows in KEEP clusters (A–H — see Phase 3).
4. **Never reuse a primary keyword.** Every primary claimed for a page/post goes in `used-keywords.md`. Check before targeting.
5. **Every image gets a descriptive filename** (not a UUID), meaningful alt text, and its generation prompt cited in the commit message.
6. **Every page has JSON-LD.** Minimum one schema type per route. See Phase 5 for the mapping.
7. **Every page has full metadata:** `title`, `description`, `openGraph.url` with hardcoded protocol+domain, `alternates.canonical`, `twitter.card`.
8. **Every deployable commit is verified twice:** locally (`curl http://localhost:3000/<route>` returns 200) then again on production after Vercel auto-deploys.

---

## Phase 0 — Discovery interview

Ask **ONE round** of structured questions (via `AskUserQuestion` when available) covering all of these. Save answers to `project_specs.md` — this becomes the source of truth for every subsequent decision.

- Client business + industry
- Positioning promise (the one thing they promise better than competitors)
- Voice preference (jargon-free / technical / formal / warm-conversational)
- Brand palette (or "help me pick from these 3 options")
- Domain (already own? need to buy? which registrar?)
- Target cities for local landing pages (0, 1, or many)
- Keyword source (Ahrefs export attached? need me to research? none needed?)
- Reference site to clone (yes/no; if yes, invoke the `clone-website` skill instead of this one)
- Content ambition (5-page brochure / brochure + blog / brochure + blog + city pages / full content operation)
- Deployment target (Vercel is default; alternatives: Netlify, Cloudflare Pages)

Do not proceed to Phase 1 until every answer is captured in `project_specs.md`.

---

## Phase 1 — Brand system

Create `brand-guidelines.md` with:

- **Palette:** 5–6 colours (primary, accent, background, text, muted, one contrast/dark). Give hex + Tailwind token names.
- **Type stack:** display font + body font + optional signature/handwriting font. Load via `next/font/google` in Phase 2.
- **Voice do's / don'ts:** 3 examples each, plain-English (`✓ "Books current in 30 days" / ✗ "Leverage synergistic accounting solutions"`).
- **Visual signature:** something distinctive that breaks the generic-SaaS look. Examples: an animated underline swoosh under key words, blob-cropped photos via CSS clip-path, hand-drawn accent lines, a signature "eyebrow" style above every section header. One signature is enough.

---

## Phase 2 — Next.js 14 scaffold

Stack: **Next.js 14 App Router + TypeScript + Tailwind CSS + Framer Motion**.

Core structure to create:

```
app/
  layout.tsx           ← fonts, Nav, Footer, root metadata, StructuredData(Organization)
  page.tsx             ← home
  globals.css          ← @layer base + brand utility classes
  {services, pricing, how-we-work, about, contact, thank-you}/page.tsx
  api/contact/route.ts ← POST endpoint (Supabase insert + Resend email, graceful skip if env unset)
  sitemap.xml/route.ts ← dynamic sitemap
components/
  design-system/{Section, Button, Card}.tsx
  signature/*.tsx      ← brand-specific visual signature components
  layout/{Nav, Footer}.tsx
  home/*.tsx           ← composable section components (Hero, ProofStrip, etc.)
  proof/*.tsx          ← trust primitives (guarantee chips, response badges, live counters)
  seo/StructuredData.tsx  ← <script type="application/ld+json">
  blog/*.tsx           ← TableOfContents, AuthorBio, RelatedPosts (see Phase 6)
lib/
  structured-data.ts   ← JSON-LD helpers (see Phase 5)
  utils.ts             ← cn() classnames helper
public/
  robots.txt
  {scenes, blog}/      ← generated images
```

Tailwind config extends with brand tokens. `globals.css` defines:

```css
@layer base { html { scroll-behavior: smooth; } body { @apply bg-cream text-graphite; } }
@layer components {
  .container-content { @apply mx-auto w-full max-w-content px-6 md:px-10; }
  .container-prose { @apply mx-auto w-full max-w-prose px-6; }
  .section { @apply py-16 md:py-24; }
  .section-eyebrow { @apply text-persimmon text-[12px] font-medium tracking-[0.08em] uppercase; }
}
```

---

## Phase 3 — Keyword clustering

**If an Ahrefs export exists** (docx/csv/xlsx):

1. Parse rows into: `keyword, intent, volume, kd, cpc_usd, serp_features, updated`
2. Cluster by topical theme + commercial intent. **Reference cluster taxonomy** — KEEP the first 8, SKIP the rest:

    | Cluster | Type | Action |
    |---|---|---|
    | A. Hire a [service provider] | KEEP | Meta + pillar post |
    | B. Service education (comparisons like "X vs Y") | KEEP | Comparison post + service copy |
    | C. Industry-specific service | KEEP | Cornerstone post |
    | D. Pricing / cost anxiety | KEEP | Transparency post |
    | E. Emergency (behind on X / need help fast) | KEEP | Empathy post |
    | F. Niche audience (solopreneur, gig, side hustle) | KEEP | Segment-specific post |
    | G. Differentiation angle (AI, automation, remote) | KEEP | Positioning post |
    | H. General industry queries | KEEP | Cover in existing pages |
    | I. Geographic gov queries (state DMV, tax lookups) | **SKIP** | Google satisfies via .gov |
    | J. Career / student / academic | **SKIP** | Wrong audience |
    | K. Adjacent product research | **SKIP** | Wrong intent |
    | L. Gaming / social / login noise | **SKIP** | Pure junk |
    | M. Competitor brand names | **SKIP** | Won't outrank + brand risk |

3. Write `keyword-clusters.csv` (KEEP rows only): `cluster, keyword, intent, volume, kd, cpc_usd, recommended_action, page_target, serp_features, updated`
4. Archive the full unfiltered CSV as `keyword-clusters-full.csv` for auditing
5. Write `SEO-content-plan.md` — a 30-day plan of 6 blog posts sequenced by highest-commercial-intent first, each with: primary keyword, secondary keywords, working headlines, H2 outline, word-count target, CTA, internal-link plan
6. Report the top-line: total volume, KEEP % vs SKIP %, top 5 highest-CPC×volume keywords
7. Create/append `used-keywords.md` at the project root

**If no keyword export exists:** run WebSearch on the industry + city + service permutations, extract volume estimates via WebFetch to Ahrefs/Semrush free tools if accessible, or ask the user to run an Ahrefs export.

---

## Phase 4 — Home + secondary pages

**Home page composition** (each is a swap-in component):

1. `Hero` — H1 with signature emphasis, primary CTA, secondary CTA, brand image or portrait
2. `ProofStrip` — 3 metrics (real numbers or seeded launch defaults, replaced by live values from Supabase later)
3. `EmotionalRecognition` — "You feel X? Here's exactly what we do about it." — 3 short quote → response pairs
4. `ServicesGrid` — 3–4 services, plain-English names, one-line deliverables
5. `MeetFounder` — single portrait + short bio + email link. Reinforces accountable-human positioning
6. `FirstThirtyDays` — 4-step numbered timeline with dates
7. `PricingPreview` — 3 transparent tiers with real dollar amounts
8. `CtaDrop` — final full-width conversion push

**Secondary pages** (each with own metadata + JSON-LD):

- `/services` — SectionHeader + optional editorial hero photo + ServicesGrid + CtaDrop
- `/pricing` — SectionHeader + PricingPreview + HonestyStrip + CtaDrop, `FAQPage` schema
- `/how-we-work` — FirstThirtyDays + Guarantees grid + CtaDrop
- `/about` — PersonalBio + 3 belief statements + CtaDrop
- `/contact` — form (react-hook-form or plain useState) + Cal.com embed
- `/thank-you` — post-submit page with lead-magnet download link

---

## Phase 5 — SEO foundation

**Every page metadata** (via Next.js `export const metadata: Metadata`):

```ts
{
  title: '<primary keyword up front, ≤60 chars>',
  description: '<value prop + specific CTA, ≤160 chars>',
  alternates: { canonical: '<route>' },
  openGraph: { title, description, url: `${SITE_URL}<route>`, type, siteName },
  twitter: { card: 'summary_large_image', title, description },
}
```

**Root layout metadata** additionally sets `metadataBase: new URL(SITE_URL)` and title template `%s | <Business Name>`.

**Site-level files:**

- `public/robots.txt` — allow all, point to sitemap, set Host
- `app/sitemap.xml/route.ts` — hand-authored ROUTES array of `{ path, priority, changefreq }`. Emit XML.

**JSON-LD by page type:**

| Page | Schema types |
|---|---|
| Root layout (all pages) | `Organization` |
| Home | `ProfessionalService` with `hasOfferCatalog` |
| `/services` | `Service` |
| `/pricing` | `FAQPage` |
| `/blog/[slug]` | `BlogPosting` + `FAQPage` + `BreadcrumbList` |
| `/locations/[city]` | `LocalBusiness` (with `City` → `AdministrativeArea` nesting) + `FAQPage` + `BreadcrumbList` |

**Search-engine verification plumbing** in `app/layout.tsx`:

```ts
metadata.verification = {
  google: process.env.GOOGLE_SITE_VERIFICATION,
  other: process.env.BING_SITE_VERIFICATION
    ? { 'msvalidate.01': process.env.BING_SITE_VERIFICATION }
    : undefined,
}
```

Env vars documented in `.env.example` with the exact Search Console click-path.

---

## Phase 6 — Blog post pipeline (per primary keyword)

For each primary keyword from the SEO plan:

1. **Check `used-keywords.md`** — abort if already claimed
2. **`WebSearch` the primary keyword** — capture the top 10 result URLs
3. **`WebFetch` top 3 pages** in parallel — extract structural map only:
    - Format type (listicle / decision framework / how-to)
    - Word count
    - H2 list in order
    - Topic coverage matrix
    - Featured-snippet answer format
    - Never reproduce prose from these pages
4. **(Optional) `WebFetch` a style reference** — extract abstract tone characteristics only (sentence rhythm, humor patterns, transition style). Never reproduce prose.
5. **Generate 3 editorial images** via Higgsfield (`mcp__88f7781e-*__generate_image`):
    - Hero (16:9, above-the-fold, `priority` hint)
    - Mid-post editorial (16:9, between sections)
    - Closing editorial (16:9)
    - Save to `public/blog/<slug>/<descriptive-name>.webp`
    - Use `seedream_v4_5` for editorial scenes (~1 credit); use `nano_banana_pro` when rearranging a user-supplied reference image
6. **Write the post** — 1800–2200 words (aim ~80% of top-3 average). Original prose only. Structure:
    - Featured-snippet **answer block** at top (persimmon-bordered card with `<strong>Short answer:</strong> ...`)
    - Named-character opening scene (clearly framed as illustrative composite, NOT a testimonial)
    - Table of contents with jump links to H2 anchors (uses `<TableOfContents items={TOC} />`)
    - Match top-3 format
    - Cover every topic top-3 covers + 1–2 they miss (usually: "when you DON'T need this yet", real dollar math where competitors hand-wave, emotional/opportunity cost angle)
    - Comparison table if a natural "X vs Y" question exists
    - Five-question checklist for practical value
    - **FAQ section** — 6 questions pulled from People Also Ask themes
    - `<AuthorBio />` card
    - `<RelatedPosts items={[...]} />` with 3 REAL internal links (no dead placeholders)
    - Final CTA drop
7. **Wire JSON-LD:** BlogPosting + FAQPage + BreadcrumbList (via `lib/structured-data.ts` helpers)
8. **Add H2 anchor `id`s** matching the TOC entries
9. **Add to sitemap** at priority 0.7, changefreq monthly
10. **Append to `used-keywords.md`** with date + URL + cluster
11. **Verify:**
    - `curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/blog/<slug>` returns 200
    - `curl -s http://localhost:3000/blog/<slug> | grep -oE '"@type":"[A-Za-z]+"' | sort -u` includes BlogPosting, FAQPage, BreadcrumbList
    - Each image file returns 200
    - Preview logs show no errors
12. **Commit** with a detailed message documenting: primary keyword + CPC×volume, research sources (top-3 URLs, style ref), image credits (model + count of credits), structural choices, and any unique angles added

---

## Phase 7 — Local landing pages (per city)

Never a template swap. Every city page is REAL local content — Google detects thin content.

1. **Primary keyword:** `"small business [service] [city]"` (or industry equivalent)
2. **Check `used-keywords.md`** and append after publish
3. **URL:** `/locations/[city-slug]`
4. **Composition** — mix reused home components with 3 net-new local components:
    - `<City>Hero` (new) — H1 with signature emphasis on service + city
    - `ProofStrip` (reused)
    - `<City>LocalTrust` (new) — 10–12 named neighborhoods in a two-column list, county framing, local tax/regulatory notes
    - `EmotionalRecognition`, `ServicesGrid`, `MeetFounder`, `FirstThirtyDays` (reused for brand consistency)
    - `<City>Faq` (new) — 5–6 questions about local tax/regulatory context, INCLUDING an "is this a real page or just SEO?" transparency question answered head-on
    - `PricingPreview`, `CtaDrop` (reused)
5. **JSON-LD:** `LocalBusiness` (with `City` → `AdministrativeArea` nesting) + `FAQPage` + `BreadcrumbList`
6. **Add to sitemap** at priority 0.8
7. **Hedge tax specifics** where rates change often (Ohio CAT threshold, city income tax rates). Publish general guidance + "we'll confirm exact numbers on the discovery call" — better than a stale figure
8. Verify + commit as per Phase 6 checklist

---

## Phase 8 — Image generation

Higgsfield via `mcp__88f7781e-*__generate_image`:

- **Default model: `seedream_v4_5`** — 1 credit per image, high quality, no reference needed. Best for editorial scenes and hero shots.
- **`nano_banana_pro`** — image-to-image capable, best for rearranging a user-supplied reference (e.g. taking a client's phone selfie and making it a brand-consistent professional portrait). Requires `medias[]` with `media_id` from `media_upload` / `media_import_url` — NOT a raw URL.

**Prompt discipline template:**

> Warm documentary-style photograph of `<subject with 2–3 concrete detail anchors>`. `<framing>` (over-the-shoulder / wide interior / close-up). `<lighting>` (natural window / golden hour / soft afternoon). `<emotional read>` (warm, unhurried, tense but determined). **No text or logos visible anywhere. No readable text on any surface.** Editorial magazine feel, muted natural colour palette, no over-saturation.

**Storage conventions:**
- Blog images: `public/blog/<slug>/<descriptive>.webp`
- Editorial scenes: `public/scenes/<descriptive>.webp`
- Portraits: `public/<person>.jpg`

**Post-generation:**
- Poll `mcp__88f7781e-*__show_generations` to get `results.rawUrl` (PNG) or `results.minUrl` (webp — prefer this for web delivery)
- `curl -sSL` the webp URL to `public/...`
- Reference via `next/image` with `priority` on above-the-fold images and `sizes` set for the responsive breakpoints

Every image gets meaningful alt text: subject + context + emotion, not "image of person".

---

## Phase 9 — Deployment

Assumes: GitHub + Vercel. Substitute equivalents (GitLab + Netlify, etc.) if the discovery answers differ.

1. **User creates GitHub repo** (you can push, not create). Ask them to name it `<business-slug>` (kebab-case) and NOT initialize with README/gitignore/license.
2. `git remote add origin https://github.com/<user>/<repo>.git && git push -u origin main`
3. **User signs into Vercel with GitHub** → Import Repository → auto-detects Next.js
4. **Env vars in Vercel dashboard** (from `.env.example`):
    - `NEXT_PUBLIC_SITE_URL` (required)
    - Supabase / Resend / Cal.com (if contact form should save + notify)
    - `GOOGLE_SITE_VERIFICATION`, `BING_SITE_VERIFICATION` (paste after Search Console verification)
5. Deploy → get `.vercel.app` URL → smoke-test every route via curl
6. **Custom domain:** prefer **nameserver delegation** over manual A record — user changes registrar nameservers to `ns1.vercel-dns.com` and `ns2.vercel-dns.com`. All DNS then lives in Vercel; user never touches registrar DNS again.
    - **GoDaddy specifically:** Airo (their new AI DNS assistant) does NOT support Vercel. Skip Airo entirely and use the "Nameservers" sub-tab under DNS
7. **Redirect direction:** apex canonical (`example.com` as Production), `www.example.com` as 308 redirect to apex. All metadata in code hardcodes `https://<apex>` — no www.
8. HTTPS auto-provisions via Let's Encrypt ~1 min after DNS resolves

**Vercel gotchas to warn user about:**
- Team Settings ≠ Project Settings — Domains live under Project Settings only
- Airo doesn't know Vercel — use Nameservers tab, not Airo Connect Domain
- Both apex + www defaulting to Production is a common mistake — verify with `curl -I https://www.<domain>` returning 308

---

## Phase 10 — Post-launch

1. **Search Console** — user follows `docs/SEARCH-CONSOLE-SETUP.md`, adds property, pastes verification value into `GOOGLE_SITE_VERIFICATION` env var, redeploys, verifies
2. **Submit `sitemap.xml`** in Search Console → left sidebar → Sitemaps → enter `sitemap.xml`
3. **Lighthouse audit** on live URL — fix any sub-100 items:
    - Performance: usually image size — ensure all are webp + Next.js Image with proper `sizes`
    - Accessibility: alt text, form labels, focus rings, colour contrast — Persimmon on Cream must pass AAA
    - Best Practices: HTTPS + no console errors + no vulnerable libs (`npm audit`)
    - SEO: metadata + robots + sitemap + descriptive link text
4. **Once ~2 weeks of baseline traffic exists**, install `evo-hq/evo` for autonomous optimisation loops (see project memory `evo_autoresearch_post_launch`)
5. **Content cadence:** blog posts weekly (Phase 6), city pages monthly (Phase 7)
6. **Never break `used-keywords.md`** — check before every new post

---

## Reusable templates

### Featured-snippet answer block
```tsx
<div className="mb-10 rounded-card border-l-4 border-persimmon bg-ivory p-6 md:p-8">
  <p className="text-body-lg text-aubergine">
    <strong>Short answer:</strong> {originalConditionalAnswer}
  </p>
</div>
```

### Blog post page.tsx skeleton
```tsx
const SLUG = 'kebab-case-slug';
const TITLE = 'Original H1-style Title';
const DESCRIPTION = '155-char meta description with concrete CTA.';
const PUBLISHED = 'YYYY-MM-DD';
const MODIFIED = 'YYYY-MM-DD';
const HERO = `/blog/${SLUG}/hero-descriptive.webp`;

const TOC = [
  { id: 'section-slug', label: 'Section label matching H2' },
  // ... one per H2
];

const FAQ = [
  { q: 'Question from PAA?', a: 'Original 2-3 sentence answer.' },
  // ... 5-6 total
];

export const metadata: Metadata = {
  title: TITLE,
  description: DESCRIPTION,
  alternates: { canonical: `/blog/${SLUG}` },
  openGraph: { title: TITLE, description: DESCRIPTION, url: `${SITE_URL}/blog/${SLUG}`, type: 'article', publishedTime: PUBLISHED, images: [{ url: `${SITE_URL}${HERO}`, ... }] },
  twitter: { card: 'summary_large_image', title: TITLE, description: DESCRIPTION },
};

export default function Post() {
  return (
    <>
      <StructuredData data={blogPostingJsonLd({ slug: SLUG, title: TITLE, description: DESCRIPTION, image: HERO, datePublished: PUBLISHED, dateModified: MODIFIED })} />
      <StructuredData data={faqPageJsonLd(FAQ)} />
      <StructuredData data={breadcrumbJsonLd([{ name: 'Home', path: '/' }, { name: 'Blog', path: '/blog' }, { name: TITLE, path: `/blog/${SLUG}` }])} />
      <article>
        {/* Hero + breadcrumb + published date + reading time */}
        {/* TableOfContents */}
        {/* Featured-snippet answer block */}
        {/* Opening scene */}
        {/* Sections with id="…" matching TOC */}
        {/* Editorial images between sections */}
        {/* FAQ */}
        {/* AuthorBio */}
        {/* RelatedPosts */}
        {/* CTA drop */}
      </article>
    </>
  );
}
```

### JSON-LD helpers signature (lib/structured-data.ts)
```ts
export function blogPostingJsonLd(post: {slug, title, description, image, datePublished, dateModified?, author?}): object
export function faqPageJsonLd(items: Array<{q: string, a: string}>): object
export function breadcrumbJsonLd(trail: Array<{name: string, path: string}>): object
export function localBusinessJsonLd(city: {name, region, regionCode, country?}): object
export const organizationJsonLd, professionalServiceJsonLd, servicesJsonLd, pricingFaqJsonLd: object
```

---

## Anti-patterns (deliberate scope limits)

- **No comment widgets** — spam vector, no SEO value
- **No fake testimonials** until real ones exist — audit + reputation risk
- **No stock photos of handshakes / skyscrapers / diverse-office-hero** — generic-SaaS smell, hurts trust
- **No jargon words:** "leverage", "holistic", "synergy", "unlock", "empower", "solution"
- **No pop-up email captures** — hurt engagement + conversion metrics
- **No dark patterns** in pricing display — transparency IS the differentiator for small-business services
- **No thin location pages** — every city page needs 3 net-new local components, not just find/replace on the city name
- **No dead placeholder links** in RelatedPosts — link only to routes that already exist and return 200
- **No Search Console verification hash invention** — Google issues unique per-property hashes; scaffold the env var and wait for the real value

---

## Success criteria (definition of done)

- All routes return 200 on the production URL
- HTTPS via Let's Encrypt, auto-provisioned
- Every page's HTML source contains at least one `"@type": "..."` JSON-LD block
- Sitemap.xml lists every real page
- `robots.txt` allows all, points to sitemap
- Zero errors in Vercel production logs
- Lighthouse target: `100 / 100 / 100 / 100` (Perf may be 90–99 acceptable with unavoidable heavy images)
- Domain: apex canonical, www 308 redirects, HTTPS everywhere
- Search Console: property verified, sitemap submitted, no crawl errors after 48 hours
- `used-keywords.md` has one entry per primary keyword targeted, no duplicates

---

## Case reference

The exemplar for this skill is **njaccountstax.com** (built 2026-07-15 to 2026-07-16, one Ben + one Claude Code session, from `git init` to live custom-domain HTTPS in a single working day). The commit history under `github.com/benji4563/nj-accounting-and-tax-services` demonstrates the phase-by-phase execution and is the authoritative reference for how these steps look when applied end-to-end.
