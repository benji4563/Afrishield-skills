#!/usr/bin/env python3
"""
gbp_competitors.py — read the Google Maps top results for a query and recommend
Google Business Profile categories from what the leaders actually use.

  Primary category    the category most of the top N (default 3) list first;
                      ties go to the #1 result.
  Secondary (max 9)   every other category used across the fetched results,
                      ranked by how many competitors use it.

Source: Apify actor compass/crawler-google-places ($0.004 per place on the free
plan). Token: APIFY_TOKEN (environment, project .env, or the shared
'00 Knowledge/Keyword Finder/.env').

Usage
  python gbp_competitors.py --query "plumber" --location "Toronto, ON"
  python gbp_competitors.py --query "plumber" --location "Toronto, ON" --depth 10 --own-name "Example Plumbing"
  python gbp_competitors.py --input-json local-seo/output/gbp_competitors_raw.json   # re-score, no fetch
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter
from pathlib import Path

from _common import load_env, out_dir, utf8_stdout, write_json

APIFY_ACTOR = "compass/crawler-google-places"
COST_PER_PLACE = 0.004
MAX_SECONDARY = 9


def fetch(query: str, location: str, depth: int, lang: str) -> list[dict]:
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        raise SystemExit("APIFY_TOKEN not set (environment, .env, or 00 Knowledge/Keyword Finder/.env).")
    try:
        from apify_client import ApifyClient
    except ImportError:
        raise SystemExit("apify-client is not installed: pip install apify-client")
    client = ApifyClient(token)
    run = client.actor(APIFY_ACTOR).call(
        run_input={"searchStringsArray": [query], "locationQuery": location,
                   "maxCrawledPlacesPerSearch": depth, "language": lang,
                   "skipClosedPlaces": True},
        timeout_secs=600)
    if not run or run.get("status") != "SUCCEEDED":
        raise SystemExit(f"Apify run did not succeed: {run.get('status') if run else 'no run'}")
    return list(client.dataset(run["defaultDatasetId"]).iterate_items())


def categories_of(place: dict) -> list[str]:
    listed = [c for c in (place.get("categories") or []) if c]
    primary = place.get("categoryName")
    if primary and primary not in listed:
        listed.insert(0, primary)
    return listed


def analyse(places: list[dict], top: int, own_name: str) -> dict:
    own = own_name.strip().lower()
    # Sponsored placements are paid, not earned, so they say nothing about what ranks.
    organic = [p for p in places if not p.get("isAdvertisement")]
    ranked = [p for p in organic if not own or own not in (p.get("title") or "").lower()]
    ranked.sort(key=lambda p: p.get("rank") or 10**6)
    leaders = ranked[:top]
    if not leaders:
        raise SystemExit("No competitor results to analyse.")

    primary_votes = Counter(p.get("categoryName") for p in leaders if p.get("categoryName"))
    if not primary_votes:
        raise SystemExit("The top results carry no category data.")
    best = max(primary_votes.values())
    tied = [c for c, n in primary_votes.items() if n == best]
    primary = next(p["categoryName"] for p in leaders if p.get("categoryName") in tied)

    usage = Counter()
    for place in ranked:
        for category in set(categories_of(place)):
            if category != primary:
                usage[category] += 1
    secondary = [{"category": c, "used_by": n, "of": len(ranked),
                  "confidence": "common" if n >= 2 else "single competitor - check it fits"}
                 for c, n in usage.most_common(MAX_SECONDARY)]

    return {
        "primary_category": primary,
        "primary_votes": dict(primary_votes),
        "secondary_categories": secondary,
        "competitors": [{
            "rank": p.get("rank"), "name": p.get("title"),
            "primary_category": p.get("categoryName"),
            "categories": categories_of(p),
            "rating": p.get("totalScore"), "reviews": p.get("reviewsCount"),
            "website": p.get("website"), "phone": p.get("phone"),
            "address": p.get("address"), "maps_url": p.get("url"),
        } for p in ranked],
        "leaders_analysed": len(leaders),
        "results_analysed": len(ranked),
    }


def main(argv=None) -> int:
    utf8_stdout()
    parser = argparse.ArgumentParser(description="Recommend GBP categories from the Google Maps leaders.")
    parser.add_argument("--query", help="What a customer searches, e.g. 'plumber'.")
    parser.add_argument("--location", help="Primary metro, e.g. 'Toronto, ON'.")
    parser.add_argument("--top", type=int, default=3, help="Leaders that vote on the primary category (default 3).")
    parser.add_argument("--depth", type=int, default=10, help="Places to fetch; billed per place (default 10).")
    parser.add_argument("--lang", default="en")
    parser.add_argument("--own-name", default="", help="Your business name, so it is not counted as a competitor.")
    parser.add_argument("--max-cost", type=float, default=0.10, help="Refuse to start above this estimate in USD (default 0.10).")
    parser.add_argument("--input-json", help="Skip fetching; analyse a saved raw file.")
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--prefix", default="gbp_competitors")
    args = parser.parse_args(argv)

    target = out_dir(args.out_dir)
    if args.input_json:
        places = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
    else:
        if not args.query or not args.location:
            parser.error("--query and --location are required unless --input-json is given")
        estimate = args.depth * COST_PER_PLACE
        if estimate > args.max_cost:
            raise SystemExit(f"Estimated ${estimate:.3f} exceeds --max-cost ${args.max_cost:.2f}. "
                             "Lower --depth or raise --max-cost.")
        load_env()
        print(f"Fetching {args.depth} Google Maps results for '{args.query}' in {args.location} "
              f"(about ${estimate:.3f})...")
        places = fetch(args.query, args.location, args.depth, args.lang)
        write_json(target / f"{args.prefix}_raw.json", places)

    report = analyse(places, args.top, args.own_name)
    write_json(target / f"{args.prefix}.json", report)
    with (target / f"{args.prefix}.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["rank", "name", "primary_category", "categories", "rating", "reviews", "website", "phone", "address"])
        for c in report["competitors"]:
            writer.writerow([c["rank"], c["name"], c["primary_category"], " | ".join(c["categories"]),
                             c["rating"], c["reviews"], c["website"], c["phone"], c["address"]])

    print(f"\nPrimary category: {report['primary_category']}  "
          f"(votes among top {report['leaders_analysed']}: {report['primary_votes']})")
    print(f"Secondary categories (max {MAX_SECONDARY}):")
    for item in report["secondary_categories"]:
        print(f"  - {item['category']}  [{item['used_by']}/{item['of']} competitors, {item['confidence']}]")
    if not report["secondary_categories"]:
        print("  (none found - competitors list a single category)")
    print(f"\nSaved {target / (args.prefix + '.json')} and .csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
