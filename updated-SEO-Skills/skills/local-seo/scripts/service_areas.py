#!/usr/bin/env python3
"""
service_areas.py — validate service areas for a service-area business (SAB).

Google's guideline: service areas should sit within about two hours' drive of
where the business is based, and a profile holds at most 20. This script
geocodes the base and every candidate area, gets the driving time, drops
anything beyond the limit and keeps the best 20.

  Geocoding   OpenStreetMap Nominatim (free, no key, one request a second)
  Drive time  OSRM public routing server (free, no key). If it is unreachable
              the script estimates from straight-line distance and says so in
              the 'method' column.

Ranking: by local search demand when --volumes is given (a keyword-map.csv
from local_keywords.py), otherwise by drive time.

Usage
  python service_areas.py                                   # base + areas from local-seo/business.json
  python service_areas.py --base "Toronto, ON" --areas "Etobicoke, ON" "Mississauga, ON" "Barrie, ON"
  python service_areas.py --volumes local-seo/output/keyword-map.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
import urllib.parse
from collections import defaultdict
from pathlib import Path

from _common import city_name, http_get, load_business, out_dir, slugify, utf8_stdout, write_json

NOMINATIM = "https://nominatim.openstreetmap.org/search"
OSRM_TABLE = "https://router.project-osrm.org/table/v1/driving/"
# Straight-line to road distance, and a mixed urban/highway average speed.
CIRCUITY, AVERAGE_KMH = 1.3, 70.0


def geocode(place: str, country: str) -> tuple[float, float] | None:
    query = {"q": place, "format": "json", "limit": 1}
    if country:
        query["countrycodes"] = country.lower()
    status, body = http_get(f"{NOMINATIM}?{urllib.parse.urlencode(query)}")
    time.sleep(1.1)  # Nominatim usage policy
    if status != 200:
        return None
    hits = json.loads(body)
    return (float(hits[0]["lat"]), float(hits[0]["lon"])) if hits else None


def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, (*a, *b))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(h))


def osrm_table(base: tuple[float, float], points: list[tuple[float, float]]):
    """Drive minutes and km from base to each point, or None if OSRM is unavailable."""
    coords = ";".join(f"{lon:.6f},{lat:.6f}" for lat, lon in [base, *points])
    status, body = http_get(f"{OSRM_TABLE}{coords}?sources=0&annotations=duration,distance", timeout=30)
    if status != 200:
        return None
    data = json.loads(body)
    if data.get("code") != "Ok":
        return None
    durations, distances = data["durations"][0][1:], data["distances"][0][1:]
    return [(d / 60 if d is not None else None, m / 1000 if m is not None else None)
            for d, m in zip(durations, distances)]


def city_volumes(path: str) -> dict[str, float]:
    totals: dict[str, float] = defaultdict(float)
    with open(path, newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            if row.get("city"):
                try:
                    totals[slugify(row["city"])] += float(row.get("cluster_volume") or row.get("volume") or 0)
                except ValueError:
                    pass
    return totals


def main(argv=None) -> int:
    utf8_stdout()
    parser = argparse.ArgumentParser(description="Validate SAB service areas against a drive-time limit.")
    parser.add_argument("--business", default=None, help="Business config (default local-seo/business.json).")
    parser.add_argument("--base", help="Where the business is based, e.g. 'Toronto, ON'.")
    parser.add_argument("--areas", nargs="*", help="Candidate service areas.")
    parser.add_argument("--country", default=None, help="Country code to bias geocoding, e.g. ca, us, cm.")
    parser.add_argument("--max-minutes", type=float, default=120, help="Drive-time limit (default 120).")
    parser.add_argument("--max-areas", type=int, default=20, help="Service areas a profile can hold (default 20).")
    parser.add_argument("--volumes", help="keyword-map.csv to rank areas by local search demand.")
    parser.add_argument("--no-route", action="store_true", help="Skip OSRM; estimate from straight-line distance.")
    parser.add_argument("--out-dir", default=None)
    args = parser.parse_args(argv)

    business = {}
    if not (args.base and args.areas):
        business = load_business(args.business)
    base_label = args.base or business.get("primary_metro") or ""
    areas = args.areas or business.get("service_areas") or []
    country = args.country or business.get("country_code") or ""
    if not base_label or not areas:
        raise SystemExit("Need a base and at least one candidate area (flags or business.json).")

    geo = business.get("geo") or {}
    if not args.base and geo.get("lat") is not None and geo.get("lng") is not None:
        base = (float(geo["lat"]), float(geo["lng"]))
    else:
        print(f"Geocoding base: {base_label}")
        base = geocode(base_label, country)
        if not base:
            raise SystemExit(f"Could not geocode the base '{base_label}'.")

    rows = []
    for area in dict.fromkeys(areas):
        print(f"Geocoding {area}")
        rows.append({"area": area, "point": geocode(area, country)})

    located = [r for r in rows if r["point"]]
    table = None if args.no_route else osrm_table(base, [r["point"] for r in located])
    if table is None and not args.no_route:
        print("OSRM unavailable - falling back to straight-line estimates.")
    for index, row in enumerate(located):
        routed = table[index] if table else (None, None)
        if routed[0] is not None:
            row["minutes"], row["km"], row["method"] = routed[0], routed[1], "osrm_route"
        else:
            km = haversine_km(base, row["point"]) * CIRCUITY
            row["minutes"], row["km"], row["method"] = km / AVERAGE_KMH * 60, km, "estimate"

    volumes = city_volumes(args.volumes) if args.volumes else {}
    for row in rows:
        row["volume"] = volumes.get(slugify(city_name(row["area"])), 0.0) if volumes else None
        if not row["point"]:
            row["status"] = "NOT_FOUND"
        elif row["minutes"] > args.max_minutes:
            row["status"] = "TOO_FAR"
        else:
            row["status"] = "OK"

    eligible = [r for r in rows if r["status"] == "OK"]
    eligible.sort(key=lambda r: (-(r["volume"] or 0), r["minutes"]) if volumes else (r["minutes"],))
    for position, row in enumerate(eligible):
        row["status"] = "KEEP" if position < args.max_areas else "OVER_LIMIT"

    order = {"KEEP": 0, "OVER_LIMIT": 1, "TOO_FAR": 2, "NOT_FOUND": 3}
    rows.sort(key=lambda r: (order[r["status"]], -(r["volume"] or 0), r.get("minutes") or 0))

    target = out_dir(args.out_dir)
    with (target / "service-areas.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["area", "status", "drive_minutes", "drive_km", "method", "monthly_volume", "lat", "lng"])
        for r in rows:
            lat, lng = r["point"] or ("", "")
            writer.writerow([r["area"], r["status"],
                             f"{r['minutes']:.0f}" if r.get("minutes") is not None else "",
                             f"{r['km']:.0f}" if r.get("km") is not None else "",
                             r.get("method", ""), "" if r["volume"] is None else f"{r['volume']:.0f}", lat, lng])
    write_json(target / "service-areas.json", {
        "base": {"label": base_label, "lat": base[0], "lng": base[1]},
        "max_minutes": args.max_minutes,
        "ranked_by": "local search volume" if volumes else "drive time",
        "areas": [{"area": r["area"], "slug": slugify(city_name(r["area"])), "status": r["status"],
                   "drive_minutes": round(r["minutes"]) if r.get("minutes") is not None else None,
                   "drive_km": round(r["km"]) if r.get("km") is not None else None,
                   "method": r.get("method"), "monthly_volume": r["volume"],
                   "lat": r["point"][0] if r["point"] else None,
                   "lng": r["point"][1] if r["point"] else None} for r in rows]})

    print(f"\n{'Area':32} {'Status':11} {'Drive':>7}  Method")
    for r in rows:
        drive = f"{r['minutes']:.0f} min" if r.get("minutes") is not None else "-"
        print(f"{r['area'][:32]:32} {r['status']:11} {drive:>7}  {r.get('method', '')}")
    kept = sum(r["status"] == "KEEP" for r in rows)
    print(f"\n{kept} of {len(rows)} areas kept (limit {args.max_areas}, within {args.max_minutes:.0f} min). "
          f"Ranked by {'local search volume' if volumes else 'drive time'}.")
    if any(r.get("method") == "estimate" for r in rows):
        print("Rows marked 'estimate' are straight-line approximations - confirm borderline ones in Google Maps.")
    print(f"Saved {target / 'service-areas.csv'} and service-areas.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
