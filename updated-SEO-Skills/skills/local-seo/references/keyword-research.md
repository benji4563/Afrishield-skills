# /keyword-research - local filter and clustering

Turns the services and cities in `business.json` into a keyword map: which
Service x City pages to build, which blog posts to write, and which money page
each post links to.

## Run it

```
python scripts/local_keywords.py seeds                              # preview the seed list, free
python scripts/local_keywords.py run --prefix <business-slug>       # fetch, filter, cluster
python scripts/local_keywords.py run --prefix <business-slug> --serp-top 20   # also read page one
python scripts/local_keywords.py filter --input <file.csv>          # filter an existing file, free
```

`run` calls the AfriShield keyword engine
(`00 Knowledge/Keyword Finder/keyword_orchestrator.py --provider auto`). That is
the company standard; do not use DataForSEO or guess figures.

**Cost, state it before running:** $0.012 per keyword row from Apify, 100 rows
by default, so about $1.20 (`--max-ideas` lowers it; the engine caps a run at
$1.50). `--serp-top 20` adds about $0.09. The Apify free plan is $5 a month.
`--provider trends` is free but returns no volume or CPC.

`filter --input` accepts an engine `<prefix>_verified.csv` or a Semrush or
Ahrefs export (columns such as Keyword, Volume, Keyword Difficulty, CPC, Intent
are recognised). If the user has an export, use it: it is free and it carries
real KD.

## The four steps

| Step | Rule | Default | Flag |
|---|---|---|---|
| 1. Search volume | monthly local searches at or above the floor | 50 | `--min-volume` (use 100 in large metros, 20-30 in small towns) |
| 2. Difficulty | low-hanging fruit only | see below | see below |
| 3. Intent | money keywords ("emergency plumber toronto") apart from informational ("how to fix water heater") | - | - |
| 4. Commercial value | a money keyword must have a CPC: someone pays for that click | any CPC | `--min-cpc` |

### Step 2 is three different metrics - say which one you used

| Metric | Source | Passes at | Flag |
|---|---|---|---|
| `kd` | link-based Keyword Difficulty, **only** in a Semrush/Ahrefs export | 30 or less | `--max-kd` |
| `serp_difficulty` | who is on page one (`--serp-top`) | 35 or less (the engine's EASY band) | `--max-serp-difficulty` |
| `competition_index` | Keyword Planner advertiser competition | 50 or less | `--max-comp-index` |

The engine has no link-based KD. Each row uses the strongest metric it has and
records it in `difficulty_metric`. These are different scales: never report
`competition_index 28` as "KD 28". For a result closest to a true KD of 30 or
less without an export, run with `--serp-top`. Rows with no metric at all are
kept and flagged `DIFFICULTY_UNCHECKED`.

### When the engine falls back to Trends

No Apify credits means no volume and no CPC, so steps 1 and 4 cannot be
applied. The script stops and says so. Options, in order: wait for credits; ask
the user for a Semrush/Ahrefs export; or re-run `filter` with
`--allow-unverified`, which keeps the keywords labelled `UNVERIFIED_NO_VOLUME`.
In that case present the map as candidate topics, with no volume claims.

## Clustering

- Every money keyword is matched to a service (its `name` or `keywords` aliases
  in `business.json`) and a city. Keywords with no city, such as "near me"
  terms, go to the primary metro.
- Per Service x City pair: the highest-volume keyword is the **primary**, the
  next 3 to 5 are **secondaries**. The page is written to rank for the group.
- `THIN_CLUSTER` means fewer than 3 secondaries. Either the page still earns
  its place on the primary alone, or the area is too small for its own page.
- Informational keywords become **blog topics**, each with `link_to`: the
  Service x City page it should pass link equity to.
- `unassigned_money_keywords` matched no service. Often that is a service the
  business offers but has not listed - ask, then add it or an alias and re-run
  `filter` (free).

## Output

`local-seo/output/keyword-map.json` and `.csv`, plus `keyword-map_rejected.csv`
with the reason each keyword was dropped.

Report to the user: counts in, kept and rejected; the page list in priority
order (cluster volume, then difficulty) with primary and secondaries; blog
topics with their link targets; thin clusters; unassigned keywords; and which
difficulty metric the numbers rest on. Have them confirm the page list before
`/service-page`.

If the client keeps a keyword pool (`keyword_pool.py`), add the run to it and
mark the chosen primaries `planned`; mark them `used` when the page ships.
