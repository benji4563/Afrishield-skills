# /gbp - Google Business Profile optimisation and audit

**Input:** business description, primary metro, core services, optional
competitor URLs - all in `local-seo/business.json`.
**Output:** `local-seo/output/gbp-plan.md`, a list the owner can work through in
the Business Profile editor. You advise and draft; the owner (or whoever holds
profile access) makes the edits. Never ask for their Google password.

## 1. Primary category - from the top 3 on Google Maps

The primary category is the strongest single ranking lever on a profile, so it
is copied from who already ranks, not reasoned from the business description.

```
python scripts/gbp_competitors.py --query "<what a customer types>" --location "<primary metro>" --own-name "<business name>"
```

- Costs about $0.04 (10 places at $0.004, Apify). Tell the user before running.
- Sponsored results are ignored. The primary is the category most of the top 3
  list first; a tie goes to the #1 result.
- If the user named competitors, check they appear in `gbp_competitors.csv`; if
  not, run a second query closer to their main service.
- No Apify credits: look the top 3 up by hand in Google Maps (each profile shows
  its primary category under the name) and record them in the plan as observed.

If the recommended primary does not describe what the business actually does,
say so and keep the honest category. A wrong category can get a profile
suspended.

## 2. Secondary categories - up to 9

The script lists every other category the fetched competitors use, by how many
use it. Keep only those the business genuinely offers. Categories marked
"single competitor - check it fits" need a reason to stay. Fewer accurate
categories beat nine loose ones; do not pad to nine.

## 3. Service areas - up to 20, within a 2-hour drive

Only for service-area businesses (`service_area_business: true`).

```
python scripts/service_areas.py --volumes local-seo/output/keyword-map.csv
```

- Geocodes each candidate and gets real drive time (OpenStreetMap + OSRM, free).
- `TOO_FAR` is beyond 120 minutes; `OVER_LIMIT` is within range but outside the
  best 20; `NOT_FOUND` could not be geocoded - fix the spelling.
- With `--volumes` the 20 are the areas with the most local search demand;
  without it they are the 20 nearest. Run `/keyword-research` first if you can.
- Rows marked `estimate` are straight-line approximations; confirm borderline
  ones in Google Maps.
- Copy `lat`/`lng` from `service-areas.json` into each Service x City page.

Write the kept areas back to `service_areas` in `business.json` and, if it was
empty, the base coordinates to `geo`.

## 4. Services and products ranked by real demand

List services in the profile in the order customers search for them.

```
python scripts/local_keywords.py run --prefix <business-slug>
```

(see `keyword-research.md` for cost and flags). From `keyword-map.json`, sum
`cluster_volume` per service and rank. For each service write a profile
description of up to 300 characters: what it is, who it is for, where - using
the cluster's primary keyword once, naturally. Services with no measurable
demand go last; do not delete a real service for lack of volume. If the run fell
back to Trends, rank by relative interest and label the list "interest, not
volume".

## 5. NAP audit and citations

Name, address and phone must be identical everywhere Google looks.

1. Find where the business is listed. Search `"<name>" "<phone>"`,
   `"<name>" "<city>"`, and check the directories that matter in its market
   (Google, Bing Places, Apple Business Connect, Facebook, Yelp, the main local
   and industry directories). Add every listing URL to `citations` in
   `business.json`.
2. Run the audit:
   ```
   python scripts/nap_audit.py
   ```
3. Read `nap-audit.csv`. `MISMATCH` rows are the priority: an old phone number
   or a JSON-LD block that disagrees. `PARTIAL` means compare by eye.
   `FETCH_FAILED` means the directory blocked the request (Yelp, Facebook and
   BBB usually do) - open it in the browser and check it yourself.
4. The area-code line checks the phone against `expected_area_codes`. A
   toll-free or out-of-area number as the primary profile number is a finding:
   recommend a local number as primary, with the other as an additional number.
5. List the major directories where the business is **not** listed. Those are
   the citations to build, each with the exact NAP string to paste.

## The plan file

Write `local-seo/output/gbp-plan.md` with, in this order: primary category and
the evidence for it; secondary categories; service areas (kept, dropped and
why); services in demand order with descriptions; NAP fixes; citations to
build; and anything that needs the owner's decision. Put real figures from the
output files next to each recommendation.

## Also check while you are there

Business name matches the real-world name exactly (no added keywords - that is a
suspension risk); hours and holiday hours; description uses its 750 characters;
at least ten recent photos; booking or quote link; the review link is in
`business.json` under `gbp.review_link`.
