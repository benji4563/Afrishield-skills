# /service-page - Service x City matrix pages

One conversion-focused page per `[Core Service] in [City/Neighbourhood]`, at
`/services/<service>/<city>`. The template is fixed; every page is a JSON data
file. A page is built only when its file says `"status": "ready"`, and a file
only reaches `ready` after the doorway gate passes it.

## Files

Install into the site with `python scripts/install.py --target <project> --templates`.

| Path in the project | Role |
|---|---|
| `content/local-seo/pages/<service>--<city>.json` | One page's content. `_example.*.json` shows every field; files starting with `_` are never built |
| `app/services/[service]/[city]/page.tsx` | The template. Static, `dynamicParams = false`: only pages with a data file exist |
| `components/local-seo/sections.tsx` | DefinitionBlock, LocalProof, LocalWork, ComparisonTable, FaqSection |
| `components/local-seo/QuoteForm.tsx`, `app/api/quote/route.ts` | Instant quote form -> `QUOTE_WEBHOOK_URL` |
| `lib/local-seo/schema.ts` | LocalBusiness, Service, FAQPage, BreadcrumbList JSON-LD |
| `lib/local-seo/pages.ts` | `serviceCitySitemapEntries()` - spread it into the site's sitemap route |

Stack: Next.js App Router (14 or later), TypeScript, Tailwind, `@/` path alias.
The components use neutral slate classes; restyle them to the site's brand
tokens. On another framework, keep the JSON files and the gate and port the
template.

## Which pages to build

Take `money_pages` from `keyword-map.json`, in order. Build a page only where
there is both demand (the cluster) and real local material (below). A service
or city with neither is not a page. Start with the 5 to 10 strongest; a matrix
of 200 thin pages is how a site earns a doorway penalty.

## What each page needs - and where it comes from

| Field | Requirement | Source |
|---|---|---|
| `primaryKeyword`, `secondaryKeywords` | from the cluster | `keyword-map.json` |
| `title` | 60 characters or fewer, primary keyword first | you |
| `metaDescription` | 50-160 characters: service, city, a reason, a route to contact | you |
| `h1` | names the service and the city | you |
| `definition` | **40-70 words**, plain fact: who, what, where, what is included. No adjectives. This is the block AI engines quote | you, from `business.json` |
| `intro` | how this business handles this service in this city | the client |
| `local.landmarks` | 3+, each with a sentence tying it to the work | research + the client |
| `local.crossStreets` | 2+ real intersections | research |
| `local.neighborhoods` | 4+ names a resident would recognise | research |
| `local.localNotes` | 60+ words on what is different here: housing stock, bylaws, permits, climate, access | research + the client |
| `testimonials` | real quotes from customers in this city, `"verified": true` | **the client only** |
| `projects` | 1+ real job in this city: problem, finding, fix, result | **the client only** |
| `comparison` | a table plus a one-sentence `summary` of its takeaway | you |
| `faqs` | 4+, at least one that is about this city | People Also Ask + the client |
| `geo`, `serviceRadiusKm` | the city's coordinates and the radius served | `service-areas.json` |

Research the local facts (search, the municipality's own site, maps) and verify
them; a wrong landmark or bylaw is worse than none. Hedge anything that changes
often, such as fees or permit thresholds, and say when it was checked.

**Testimonials and project histories are never written by you.** Ask the client
for them per city. A page needs at least one verified testimonial or one real
project; with neither it stays a draft. Unverified testimonials do not render
and fail the gate.

## The anti-doorway gate

```
python scripts/doorway_check.py
```

It enforces the table above, rejects placeholder text, and compares every pair
of pages: place names are masked, then the unique copy (definition, intro,
local notes, FAQ answers, project summaries) is compared by 4-word shingles.
50% overlap fails, 30% warns. A page that is another page with the city swapped
scores near 100%.

When a page fails on similarity, rewrite from the local facts outward; do not
paraphrase the other page. The definition block is the one place a shared
structure is expected.

Only after the gate prints `PASS` for a file, set its `"status": "ready"`. Run
the gate again before every deploy (`--all` also fails drafts).

## What the template guarantees

- **Above the fold:** H1, the definition block, a click-to-call `tel:` link and
  the quote form.
- **JSON-LD in the server HTML:** `LocalBusiness` (NAP and exact coordinates
  from `business.json`), `Service` (provider, `areaServed` as the named City
  plus a `GeoCircle` boundary of `serviceRadiusKm` around the page's own
  coordinates), `FAQPage` built from the same array the visible FAQ renders,
  and `BreadcrumbList`.
- **Each section opens with a direct answer**, then detail; the comparison is a
  real `<table>` with header cells; the FAQ is plain headings and paragraphs,
  not a JavaScript accordion.
- **Visible NAP** at the foot, identical to the JSON-LD.
- **Internal links** to the same service in nearby cities and other services in
  the same city.
- Drafts are previewable in `next dev` with `noindex`; production builds and
  the sitemap include `ready` pages only.

A service-area business with `hide_address: true` publishes locality only, no
street address, in both the visible NAP and the schema.

## Verify

```
npm run build
python scripts/geo_audit.py --url http://localhost:3000/services/<service>/<city>
```

The audit must show no `FAIL`. Then add `serviceCitySitemapEntries()` to the
sitemap, log the primary keyword as used, and link the new page from the
service hub and from at least one blog post (`/blog-post`).
