# /seo-optimize and /audit - technical, on-page and GEO engine

One script, two modes of use:

- **`/audit`** - run it, report what it found, change nothing.
- **`/seo-optimize`** - run it, fix every `FAIL` and reasonable `WARN` in the
  code, run it again, repeat until clean.

For a scored, client-facing audit with competitor benchmarks, use the
`website-audit` skill instead; this one is the engineering gate.

## Run it

```
python scripts/geo_audit.py --url http://localhost:3000/services/<service>/<city>   # one page, pre-deploy
python scripts/geo_audit.py --site https://example.com --max-pages 25                # robots, sitemap and its pages
python scripts/geo_audit.py --site https://example.com --psi                         # plus Lighthouse via PageSpeed Insights
python scripts/geo_audit.py --lighthouse-json lighthouse-report.json                 # check a local Lighthouse run
```

It reads the **raw server HTML** - what AI crawlers see, since most do not run
JavaScript - so it works on `next start` locally. Output:
`local-seo/output/seo-geo-audit.md` and `.json`. Exit code 1 on any `FAIL`.

## What is checked and how to fix it

### Lighthouse and Core Web Vitals - target 90+ in all four categories

`--psi` needs a public URL (set `PSI_API_KEY` to avoid the shared quota). For
localhost:

```
npx lighthouse http://localhost:3000/<path> --output=json --output-path=lighthouse-report.json --chrome-flags="--headless"
```

| Metric | Limit | Usual fix |
|---|---|---|
| LCP | 2.5 s | hero image as WebP/AVIF via `next/image` with `priority` and correct `sizes`; no client-side data fetch above the fold |
| CLS | 0.1 | width and height on every image and embed; `next/font`; no content injected above existing content |
| INP (lab: TBT) | 200 ms | fewer and smaller client components; defer third-party scripts with `next/script` `lazyOnload`; no heavy handlers on input |

INP replaced FID as a Core Web Vital in 2024; lab runs report Total Blocking
Time as its stand-in.

### Technical

| Check | Fix |
|---|---|
| HTTP 200, indexable | remove stray `noindex`; drafts keep it deliberately |
| canonical | absolute URL of the page itself |
| viewport, `html lang` | root layout |
| robots.txt | reachable, declares the sitemap, does **not** block AI crawlers |
| sitemap.xml | valid XML, same-host URLs only, every published page listed |

**AI crawlers** that must not be blocked, and should be named: `GPTBot`,
`OAI-SearchBot`, `ChatGPT-User`, `ClaudeBot`, `Claude-SearchBot`,
`PerplexityBot`, `Google-Extended`. The robots.txt block is in the
`ai-seo-website-builder` skill, section G1.

**Search Console readiness** (the user does the console steps): verification
via the `GOOGLE_SITE_VERIFICATION` env var - never invent the value; sitemap
submitted; after deploy, URL Inspection on one Service x City page shows "URL
is on Google" or a clean "Crawled" state with the canonical the page declares.

### On-page

Title present and 60 characters or fewer; meta description 50-160; exactly one
H1; alt text on images; a `tel:` link on service and location pages.

### Schema

- Every JSON-LD block parses.
- `LocalBusiness` (or a subtype): name, url, telephone or address,
  `areaServed`, `geo` coordinates.
- `Service`: name, provider, `areaServed`.
- **`FAQPage` verified:** every question has an answer, and every question in
  the markup is visible on the page. Markup for hidden or absent questions is a
  structured-data violation. Build the JSON-LD from the array the page renders.

After deploy, confirm one page of each type in Google's Rich Results Test.

### GEO - being quotable by AI Overviews, ChatGPT Search, Perplexity and Claude

| Check | Standard |
|---|---|
| Content without JavaScript | 300+ words in the server HTML |
| Definition block | the first paragraph after the H1 is 40-70 words of plain fact: who, what, where, what is included. No marketing adjectives, no "we are proud" |
| Sections open with a direct answer | under each H2, a 12-80 word paragraph that answers the heading before any detail (target: 60% of sections or more) |
| Lists or tables | steps as lists; any "X vs Y" or "which option" as a real `<table>` with a caption and header cells |
| Comparison table | present on service and location pages |

Write for extraction: one idea per paragraph, the entity named in full (not
"we" or "it") in sentences meant to be quoted, numbers with units, dates on
anything that changes.

### Links

Blog pages must link to at least one money page. By default that means a
`/services/...` or `/locations/...` path, the layout this suite generates. A site
built differently lists its own in `money_page_paths` in `business.json` (for
example `["/pricing", "/solutions"]`) or passes `--money-path pricing` once per
path (the leading slash is optional - leave it off in Git Bash, which rewrites
`/pricing` into a Windows path); the money-page checks (FAQPage, comparison table, click-to-call) then apply
to those paths instead.

## Reporting

Lead with the counts, then every `FAIL` with its fix, then `WARN`s worth
acting on. For `/seo-optimize`, list what you changed and attach the clean
re-run. A `WARN` you chose to leave gets one line of reasoning.
