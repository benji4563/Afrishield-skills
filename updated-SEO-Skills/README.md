# Local SEO Suite

A Claude Code skill (`local-seo`) with ten slash commands that take a local or
service-area business from Google Business Profile to ranking pages, reviews
and AI-search visibility. Generic: nothing in this folder belongs to a client.

```
.claude-plugin/            plugin + marketplace manifests
commands/                  the ten slash commands (thin wrappers)
skills/local-seo/
  SKILL.md                 router, shared rules, environment variables
  references/              one procedure per module
  scripts/                 Python helpers (standard library; gbp_competitors needs apify-client)
  templates/
    business.example.json  the business file every module reads
    review-form/review.html            standalone review form
    nextjs/                Service x City page, review page, API routes, schema helpers
```

## Install into a business's project

Run from PowerShell. `<project>` is the client's site or workspace folder.

```bash
python "C:\Users\hp\Documents\AFRISHIELD\01 Skills\updated-SEO-Skills\skills\local-seo\scripts\install.py" --target "<project>"
```

For a Next.js site, add the page templates too (existing files are kept unless
you add `--force`):

```bash
python "C:\Users\hp\Documents\AFRISHIELD\01 Skills\updated-SEO-Skills\skills\local-seo\scripts\install.py" --target "<project>" --templates
```

That copies the skill to `<project>\.claude\skills\local-seo`, the commands to
`<project>\.claude\commands`, and creates `<project>\local-seo\business.json`.
Then:

1. Fill in `local-seo\business.json` (name, phone, address, services, service
   areas, Google review link).
2. Put webhook URLs and API keys in `<project>\.env` - the list is in `SKILL.md`.
3. Open Claude Code in `<project>` and run the commands below.

The keyword engine needs `pip install requests apify-client pytrends` once, and
the project must sit inside the AfriShield folder (or set `AFRISHIELD_ROOT`).

## The pipeline

Each command can be typed in Claude Code as shown. Underneath each is the
script it drives, which you can also run yourself from the project root. `S`
stands for `.claude\skills\local-seo\scripts`.

### 1. `/gbp` - Google Business Profile

```
/gbp
```

```bash
python S\gbp_competitors.py --query "plumber" --location "Toronto, ON" --own-name "Example Plumbing"
```
```bash
python S\service_areas.py --volumes local-seo\output\keyword-map.csv
```
```bash
python S\nap_audit.py
```

Result: `local-seo\output\gbp-plan.md` - primary category (from the Maps top
3), up to 9 secondary categories, up to 20 service areas inside a 2-hour drive,
services in demand order, NAP fixes and citations to build.
Cost: about $0.04 of Apify credit for the competitor lookup; the rest is free.

### 2. `/review-engine` - reviews

```
/review-engine
```

Installs the star-rating page at `/review` (or the standalone
`review-form\review.html`) and walks through the two Make.com scenarios:
private 1-3 star feedback to Slack, and replies to public Google reviews
(automatic for 4-5 stars, a Slack alert for a human reply on 1-3).

### 3. `/gbp-posts` - a month of profile posts

```
/gbp-posts 2026-11-02 3
```

```bash
python S\gbp_posts.py plan --start 2026-11-02 --per-week 3
```
```bash
python S\gbp_posts.py validate
```
```bash
python S\gbp_posts.py send
```
```bash
python S\gbp_posts.py send --send
```

`send` alone is a dry run. `--send` dispatches to `MAKE_GBP_POST_WEBHOOK_URL`.

### 4. `/keyword-research` - filter and cluster

```
/keyword-research
/keyword-research C:\path\to\semrush-export.csv
```

```bash
python S\local_keywords.py seeds
```
```bash
python S\local_keywords.py run --prefix example-plumbing --serp-top 20
```
```bash
python S\local_keywords.py filter --input semrush-export.csv --min-volume 100
```

Result: `local-seo\output\keyword-map.json` and `.csv` - Service x City pages
(primary keyword plus 3-5 secondaries each) and blog topics with the money page
each links to. Cost: about $1.20 per `run` (Apify); `filter` is free.

### 5. `/service-page` - Service x City pages

```
/service-page drain cleaning in Etobicoke
/service-page all
```

```bash
python S\doorway_check.py
```

Each page is a file in `content\local-seo\pages\<service>--<city>.json`. A page
is built only when it is marked `ready`, and only mark it ready after
`doorway_check.py` prints `PASS`.

### 6. `/blog-post` - local posts

```
/blog-post spring drain checklist etobicoke
```

### 7. `/seo-optimize` and `/audit`

```
/audit https://example.com
/seo-optimize http://localhost:3000/services/drain-cleaning/etobicoke
```

```bash
python S\geo_audit.py --url http://localhost:3000/services/drain-cleaning/etobicoke
```
```bash
python S\geo_audit.py --site https://example.com --max-pages 25 --psi
```

Result: `local-seo\output\seo-geo-audit.md`. `/audit` reports; `/seo-optimize`
fixes and re-runs until there is no `FAIL`.

### 8. `/publish` and `/syndicate`

```
/publish preview
/publish prod
/syndicate https://example.com/blog/spring-drain-checklist-etobicoke
```

```bash
vercel --prod
```
```bash
python S\syndicate.py accounts
```
```bash
python S\syndicate.py validate local-seo\social\spring-drain-checklist-etobicoke.json
```
```bash
python S\syndicate.py send local-seo\social\spring-drain-checklist-etobicoke.json --send
```

`send` without `--send` is a dry run.

## Decisions built into the suite

- **Keyword data comes from the AfriShield keyword engine**, not Semrush. It
  has no link-based KD, so the "KD 30 or less" step uses real KD when you supply
  a Semrush or Ahrefs export, otherwise page-one difficulty or Keyword Planner
  competition, and every row says which.
- **The review form keeps the Google link visible to low raters.** Showing it
  only to happy customers is "review gating", which Google's review policy
  prohibits. The setting is `publicLinkForAll`.
- **Nothing is sent without `--send`**, and paid lookups print their cost first.
- **Testimonials and case studies are never generated.** Pages without real
  local proof stay drafts.

## Verified

Checked on 2026-10-09 against sample data: the keyword filter and clustering
(a Semrush-style export and the engine's own output), drive-time validation
(live OpenStreetMap/OSRM), the competitor category analysis (saved sample
data), the posts planner and validator, the doorway gate (it failed a
city-swapped page at 100% overlap), the NAP audit, the syndication validator,
and the Next.js templates (type-check and production build on Next.js 16; the
generated page passed all 20 audit checks).

Not exercised, because they spend money or publish: the live Apify calls in
`gbp_competitors.py` and `local_keywords.py run`, real Make.com and Blotato
dispatch, the PageSpeed Insights call, and a Vercel deploy.
