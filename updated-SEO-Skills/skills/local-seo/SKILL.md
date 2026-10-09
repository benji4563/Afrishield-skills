---
name: local-seo
description: >
  Local SEO, website generation and GEO (generative engine optimisation) suite for
  any local or service-area business. Ten modules, each also a slash command:
  /gbp (Google Business Profile categories, service areas, services ranked by
  demand, NAP and citation audit), /review-engine (star-rating intake form, Slack
  alerts, review replies via Make.com), /gbp-posts (a month of scheduled profile
  posts), /keyword-research (4-step local filter and clustering), /service-page
  (Service x City matrix pages with an anti-doorway gate), /blog-post (local
  topical-authority posts that link to money pages), /seo-optimize and /audit
  (technical, on-page, schema and AI-citation checks), /publish (GitHub + Vercel)
  and /syndicate (LinkedIn, X, Facebook via Blotato). Use this skill whenever the
  user wants to rank a local business on Google Maps or local search, optimise a
  Google Business Profile, collect or reply to reviews, build city or service-area
  pages, write local blog content, audit a local site for SEO or AI search, or run
  any of the commands above - even if they only say "local SEO for [business]".
argument-hint: "<module> [business or target]"
user-invocable: true
---

# Local SEO Suite

One pipeline, ten modules. Each module has a reference file with the full
procedure; read only the one you are running.

| Command | Module | Reference | Script |
|---|---|---|---|
| `/gbp` | Google Business Profile optimisation and audit | `references/gbp.md` | `gbp_competitors.py`, `service_areas.py`, `nap_audit.py` |
| `/review-engine` | Review intake, Slack alerts, review replies | `references/review-engine.md` | templates only |
| `/gbp-posts` | A month of scheduled profile posts | `references/gbp-posts.md` | `gbp_posts.py` |
| `/keyword-research` | 4-step local filter and clustering | `references/keyword-research.md` | `local_keywords.py` |
| `/service-page` | Service x City matrix pages | `references/service-page.md` | `doorway_check.py` |
| `/blog-post` | Local topical-authority posts | `references/blog-post.md` | `geo_audit.py` (link check) |
| `/seo-optimize`, `/audit` | Technical, on-page and GEO engine | `references/seo-geo-audit.md` | `geo_audit.py` |
| `/publish`, `/syndicate` | Deployment and social distribution | `references/publish-syndicate.md` | `syndicate.py` |

Scripts are in `scripts/` and templates in `templates/`, both next to this file.
Scripts are Python 3, standard library only (`gbp_competitors.py` also needs
`apify-client`). Run them from the **project root** of the business being worked
on; they read `local-seo/business.json` and write to `local-seo/output/`.

## Recommended order

```
/gbp -> /review-engine -> /gbp-posts          Google Maps (results in weeks)
/keyword-research -> /service-page -> /blog-post -> /seo-optimize
/audit -> /publish -> /syndicate              organic and AI search
```

`/keyword-research` feeds three other modules (service ranking in `/gbp`, the
page matrix, blog topics), so on a new business run it early and re-run `/gbp`
step 4 afterwards.

## Step 0 - the business file

Everything reads `local-seo/business.json`. If it is missing, copy
`templates/business.example.json` there (or run `scripts/install.py`) and fill
it in with the user before any module runs. It is the single source of truth for
Name, Address and Phone: the website templates, the JSON-LD and the NAP audit
all read it, which is what keeps them identical.

Ask the user for anything you cannot verify: legal name, phone, address, whether
the address is hidden (service-area business), the Google review link. Never
guess these.

Secrets go in the project's `.env` (git-ignored), never in `business.json`:

| Variable | Used by |
|---|---|
| `MAKE_REVIEW_WEBHOOK_URL` | review form -> Slack |
| `QUOTE_WEBHOOK_URL` | quote form on service pages |
| `MAKE_GBP_POST_WEBHOOK_URL` | `gbp_posts.py send` |
| `MAKE_WEBHOOK_API_KEY` | optional, sent as `x-make-apikey` |
| `BLOTATO_API_KEY`, `BLOTATO_*_ACCOUNT_ID`, `BLOTATO_*_PAGE_ID` | `syndicate.py` |
| `SOCIAL_WEBHOOK_URL` | `syndicate.py --via webhook` |
| `PSI_API_KEY` | optional, `geo_audit.py --psi` |
| `APIFY_TOKEN` | already set in `00 Knowledge/Keyword Finder/.env`; do not copy it |

## Rules that hold in every module

1. **Never invent data.** No made-up search volumes, review quotes, phone
   numbers, addresses, prices, licence numbers or case studies. If the keyword
   engine fell back to Google Trends there is no volume or CPC - say so.
   Testimonials are pasted from the client or left out.
2. **Keyword data comes from the AfriShield keyword engine**
   (`00 Knowledge/Keyword Finder/keyword_orchestrator.py`, wrapped by
   `local_keywords.py`). Do not use DataForSEO for keyword ideas, volume, CPC or
   competition. A Semrush or Ahrefs export supplied by the user is welcome and is
   the only source of true link-based KD.
3. **Anything that leaves the machine is a dry run first.** `gbp_posts.py send`
   and `syndicate.py send` print what would go out and send nothing until
   `--send` is added. Show the user the dry run and get a yes before sending,
   pushing to GitHub, or deploying. Paid API calls (Apify) print their cost
   first; state it and stay under the caps.
4. **No doorway pages.** A Service x City page ships only after
   `doorway_check.py` passes it. A city-name swap is not a page.
5. **Google's review policy applies.** The review form keeps the Google link
   available to every customer, whatever they rated. Do not remove it (see
   `references/review-engine.md`).
6. **Client-specific material stays in the client's folder.** This skill is a
   template; nothing about a particular client is written back into it.
7. **Server HTML is the product.** AI crawlers mostly do not run JavaScript.
   Copy, FAQs and JSON-LD must be in the raw HTML; check with `geo_audit.py`,
   not by looking at the rendered page.

## Running a module

1. Read `local-seo/business.json`.
2. Read the module's reference file and follow it.
3. Run the script, read its output files, and report: what was found, what you
   recommend, what needs the user's decision or action. Quote real numbers from
   the output files.

Related skills: `ai-seo-website-builder` builds the base site this suite extends;
`city-landing-pages` builds city-only pages from a keyword export;
`seo-blog-humor-style` sets the blog voice; `website-audit` produces the
client-facing scored audit.
