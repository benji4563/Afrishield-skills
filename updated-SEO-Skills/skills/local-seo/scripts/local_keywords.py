#!/usr/bin/env python3
"""
local_keywords.py — local keyword research: seeds -> metrics -> 4-step filter -> clusters.

Subcommands
  seeds    Build the service x city seed list from business.json.
  run      Fetch metrics for those seeds through the AfriShield keyword engine
           (00 Knowledge/Keyword Finder/keyword_orchestrator.py, --provider auto),
           optionally check page one with serp_competition.py, then filter.
  filter   Apply the 4-step filter and clustering to an existing file: an engine
           <prefix>_verified.csv (plus <prefix>_serp.csv if present) or a
           Semrush / Ahrefs keyword export.

The 4-step filter
  1. Volume       monthly searches >= --min-volume (default 50)
  2. Difficulty   the best metric each row has, in this order:
                    kd               link-based KD from a Semrush/Ahrefs export   <= --max-kd (30)
                    serp_difficulty  page-one strength from serp_competition.py   <= --max-serp-difficulty (35)
                    competition_index  Keyword Planner ad competition             <= --max-comp-index (50)
                  The engine has no link-based KD, so the metric used is written
                  to 'difficulty_metric' on every row. They are different scales.
  3. Intent       money (Transactional / Commercial) vs informational
  4. Commercial   money keywords need a CPC >= --min-cpc, i.e. someone pays for the click

Clustering: every money keyword is assigned to a (service, city) pair; the
highest-volume keyword becomes the page's primary and the next 3-5 its
secondaries. Informational keywords become blog topics, each linked to the
service x city page it should pass link equity to.

Never invents metrics: a Trends-fallback run has no volume or CPC, so steps 1
and 4 cannot pass and the script stops unless --allow-unverified is given.

Usage
  python local_keywords.py seeds
  python local_keywords.py run --prefix example-plumbing --serp-top 20
  python local_keywords.py filter --input local-seo/output/example-plumbing_verified.csv
  python local_keywords.py filter --input semrush-export.csv --min-volume 100
"""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

from _common import city_name, keyword_finder_dir, load_business, out_dir, slugify, utf8_stdout, write_json

MONEY_INTENTS = {"transactional", "commercial"}
INFO_PATTERN = re.compile(
    r"^(how|what|why|when|where|who|which|can|does|do|is|are|should|will)\b"
    r"|\b(how to|what is|diy|ideas|tips|guide|tutorial|meaning|definition|examples?|checklist|rules|permit|bylaw|vs)\b")
STOPWORDS = {"a", "an", "the", "in", "for", "to", "of", "and", "near", "me", "my", "is", "do", "i", "on", "at", "with"}
COLUMNS = {
    "keyword": ["keyword", "query", "search term"],
    "volume": ["search_volume_or_interest", "volume", "search volume", "kp_volume", "avg. monthly searches"],
    "kd": ["kd", "keyword difficulty", "difficulty", "kd %"],
    "serp_difficulty": ["serp_difficulty"],
    "competition_index": ["competition_index", "kp_competition", "competitive density", "competition"],
    "cpc": ["high_cpc_usd", "cpc", "cpc (usd)", "kp_cpc", "cpc_usd"],
    "low_cpc": ["low_cpc_usd"],
    "intent": ["search_intent", "intent", "intents"],
    "data_source": ["data_source"],
}


def number(value) -> float | None:
    if value is None:
        return None
    text = str(value).replace(",", "").replace("$", "").replace("%", "").strip()
    try:
        return float(text)
    except ValueError:
        return None


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        sample = handle.read(4096)
        handle.seek(0)
        delimiter = ";" if sample.count(";") > sample.count(",") else ("\t" if sample.count("\t") > sample.count(",") else ",")
        reader = csv.DictReader(handle, delimiter=delimiter)
        lookup = {(name or "").strip().lower(): name for name in (reader.fieldnames or [])}
        mapping = {field: next((lookup[a] for a in aliases if a in lookup), None) for field, aliases in COLUMNS.items()}
        if not mapping["keyword"]:
            raise SystemExit(f"{path}: no keyword column found (looked for {COLUMNS['keyword']}).")
        rows = []
        for raw in reader:
            row = {field: (raw.get(column) or "").strip() if column else "" for field, column in mapping.items()}
            row["keyword"] = " ".join(row["keyword"].lower().split())
            if not mapping["volume"] and not row["data_source"]:
                row["data_source"] = "no_volume_column"
            if row["keyword"]:
                rows.append(row)
    return rows


def merge_serp(rows: list[dict], serp_path: Path) -> int:
    serp = {r["keyword"]: r for r in read_rows(serp_path)}
    merged = 0
    for row in rows:
        hit = serp.get(row["keyword"])
        if hit and hit["serp_difficulty"]:
            row["serp_difficulty"] = hit["serp_difficulty"]
            merged += 1
    return merged


def stem(word: str) -> str:
    """Crude stemmer: 'unclogging', 'clogged' and 'unclog' must meet in the middle."""
    root = re.sub(r"(ing|ed|ers|er|es|s)$", "", word) if len(word) > 4 else word
    root = re.sub(r"([b-df-hj-np-tv-z])\1$", r"\1", root)
    return root or word


def tokens(text: str) -> set[str]:
    return {stem(w) for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS}


def build_matchers(business: dict):
    services = []
    for service in business.get("services") or []:
        phrases = [service["name"], *(service.get("keywords") or [])]
        services.append((service.get("slug") or slugify(service["name"]), service["name"],
                         [tokens(p) for p in phrases if p]))
    cities = []
    for area in [business.get("primary_metro", ""), *(business.get("service_areas") or [])]:
        name = city_name(area)
        if name and slugify(name) not in {c[0] for c in cities}:
            cities.append((slugify(name), name, name.lower()))
    cities.sort(key=lambda c: -len(c[2]))  # "north york" before "york"
    return services, cities


def match_service(keyword: str, services) -> tuple[str, str]:
    words = tokens(keyword)
    best, best_size = ("", ""), 0
    for slug, name, phrase_sets in services:
        for phrase in phrase_sets:
            if phrase and phrase <= words and len(phrase) > best_size:
                best, best_size = (slug, name), len(phrase)
    return best


def match_city(keyword: str, cities) -> tuple[str, str]:
    for slug, name, needle in cities:
        if re.search(rf"\b{re.escape(needle)}\b", keyword):
            return slug, name
    return "", ""


def classify(row: dict) -> str:
    intent = row["intent"].lower()
    if any(word in intent for word in MONEY_INTENTS):
        return "money"
    if "informational" in intent:
        return "informational"
    return "informational" if INFO_PATTERN.search(row["keyword"]) else "money"


def difficulty_of(row: dict, args) -> tuple[str, float | None, bool]:
    """(metric name, value, passes). Uses the strongest metric the row carries."""
    kd = number(row["kd"])
    if kd is not None:
        return "kd", kd, kd <= args.max_kd
    serp = number(row["serp_difficulty"])
    if serp is not None:
        return "serp_difficulty", serp, serp <= args.max_serp_difficulty
    comp = number(row["competition_index"])
    if comp is not None:
        if comp <= 1 and "." in row["competition_index"]:
            comp *= 100  # Semrush competitive density is 0-1
        return "competition_index", comp, comp <= args.max_comp_index
    return "none", None, True


def run_filter(rows: list[dict], business: dict, args) -> dict:
    services, cities = build_matchers(business)
    primary_city = cities[0] if cities else ("", "", "")
    unverified = [r for r in rows if r["data_source"] and r["data_source"] != "apify_exact"]
    if unverified and not args.allow_unverified:
        raise SystemExit(
            f"{len(unverified)} of {len(rows)} rows came from the Trends/Autocomplete fallback: they have no "
            "search volume or CPC, so the volume and commercial-value steps cannot be applied.\n"
            "Re-run with Apify credits or supply a Semrush/Ahrefs export. To keep them anyway, labelled "
            "UNVERIFIED and with no metrics claimed, add --allow-unverified.")

    kept, rejected = [], []
    for row in rows:
        exact = not row["data_source"] or row["data_source"] == "apify_exact"
        volume = number(row["volume"]) if exact else None
        cpc = number(row["cpc"]) if exact else None
        metric, difficulty, difficulty_ok = difficulty_of(row, args)
        kind = classify(row)
        service = match_service(row["keyword"], services)
        city = match_city(row["keyword"], cities)
        record = {
            "keyword": row["keyword"], "type": kind, "volume": volume, "cpc": cpc,
            "difficulty_metric": metric, "difficulty": difficulty,
            "service": service[0], "service_name": service[1], "city": city[0], "city_name": city[1],
            "verified": exact, "notes": [],
        }
        reason = ""
        if exact and (volume is None or volume < args.min_volume):
            reason = f"step 1: volume {volume if volume is not None else 'missing'} < {args.min_volume}"
        elif not difficulty_ok:
            reason = f"step 2: {metric} {difficulty:.0f} over the limit"
        elif kind == "money" and exact and (cpc is None or cpc < args.min_cpc):
            reason = f"step 4: CPC {cpc if cpc is not None else 'missing'} < {args.min_cpc} - no paid competition"
        if reason:
            rejected.append({**record, "reason": reason})
            continue
        if metric == "none":
            record["notes"].append("DIFFICULTY_UNCHECKED")
        if not exact:
            record["notes"].append("UNVERIFIED_NO_VOLUME")
        kept.append(record)

    def strength(r):
        return (-(r["volume"] or 0), r["difficulty"] if r["difficulty"] is not None else 999, r["keyword"])

    # Money keywords -> one cluster per service x city page.
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    unassigned = []
    for record in (r for r in kept if r["type"] == "money"):
        if not record["service"]:
            unassigned.append(record)
            continue
        if not record["city"]:
            # "plumber near me" style terms belong to the primary metro page.
            record["city"], record["city_name"] = primary_city[0], primary_city[1]
            record["notes"].append("NO_CITY_IN_KEYWORD")
        groups[(record["service"], record["city"])].append(record)

    money_pages = []
    for (service, city), members in groups.items():
        members.sort(key=strength)
        primary, secondaries = members[0], members[1:1 + args.max_secondary]
        flags = []
        if len(secondaries) < args.min_secondary:
            flags.append(f"THIN_CLUSTER ({len(secondaries)} secondaries, target {args.min_secondary}-{args.max_secondary})")
        money_pages.append({
            "page_type": "service_city", "service": service, "service_name": primary["service_name"],
            "city": city, "city_name": primary["city_name"],
            "path": f"/services/{service}/{city}",
            "primary_keyword": primary["keyword"], "volume": primary["volume"], "cpc": primary["cpc"],
            "difficulty_metric": primary["difficulty_metric"], "difficulty": primary["difficulty"],
            "secondary_keywords": [m["keyword"] for m in secondaries],
            "cluster_volume": sum(m["volume"] or 0 for m in [primary, *secondaries]),
            "overflow_keywords": [m["keyword"] for m in members[1 + args.max_secondary:]],
            "flags": flags + sorted({n for m in [primary, *secondaries] for n in m["notes"]}),
        })
    money_pages.sort(key=lambda p: -p["cluster_volume"])
    paths = {(p["service"], p["city"]): p["path"] for p in money_pages}

    # Informational keywords -> blog topics, greedily grouped by shared words.
    info = sorted((r for r in kept if r["type"] == "informational"), key=strength)
    topics: list[dict] = []
    for record in info:
        words = tokens(record["keyword"])
        home = None
        for topic in topics:
            overlap = len(words & topic["_tokens"]) / max(1, len(words | topic["_tokens"]))
            if overlap >= 0.5 and len(topic["secondary_keywords"]) < args.max_secondary:
                home = topic
                break
        if home:
            home["secondary_keywords"].append(record["keyword"])
            home["cluster_volume"] += record["volume"] or 0
            continue
        links = []
        if record["service"]:
            same_service = [p for p in money_pages if p["service"] == record["service"]]
            exact_page = paths.get((record["service"], record["city"]))
            links = [exact_page] if exact_page else [p["path"] for p in same_service[:2]]
        topics.append({
            "page_type": "blog_post", "primary_keyword": record["keyword"], "volume": record["volume"],
            "difficulty_metric": record["difficulty_metric"], "difficulty": record["difficulty"],
            "service": record["service"], "city": record["city"], "city_name": record["city_name"],
            "secondary_keywords": [], "cluster_volume": record["volume"] or 0,
            "link_to": links, "flags": list(record["notes"]) + ([] if links else ["NO_MONEY_PAGE_TO_LINK"]),
            "_tokens": words,
        })
    for topic in topics:
        del topic["_tokens"]

    return {
        "thresholds": {"min_volume": args.min_volume, "max_kd": args.max_kd,
                       "max_serp_difficulty": args.max_serp_difficulty,
                       "max_comp_index": args.max_comp_index, "min_cpc": args.min_cpc},
        "counts": {"input": len(rows), "kept": len(kept), "rejected": len(rejected),
                   "money_pages": len(money_pages), "blog_topics": len(topics),
                   "unassigned_money": len(unassigned)},
        "money_pages": money_pages, "blog_topics": topics,
        "unassigned_money_keywords": [{"keyword": r["keyword"], "volume": r["volume"], "cpc": r["cpc"]}
                                      for r in sorted(unassigned, key=strength)],
        "rejected": [{"keyword": r["keyword"], "reason": r["reason"]} for r in rejected],
    }


def write_map(result: dict, target: Path, prefix: str) -> None:
    write_json(target / f"{prefix}.json", result)
    with (target / f"{prefix}.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["page_type", "path_or_topic", "service", "city", "primary_keyword", "volume", "cpc",
                         "difficulty_metric", "difficulty", "secondary_keywords", "cluster_volume", "link_to", "flags"])
        for page in result["money_pages"]:
            writer.writerow(["service_city", page["path"], page["service"], page["city_name"], page["primary_keyword"],
                             page["volume"], page["cpc"], page["difficulty_metric"], page["difficulty"],
                             " | ".join(page["secondary_keywords"]), page["cluster_volume"], "", " | ".join(page["flags"])])
        for topic in result["blog_topics"]:
            writer.writerow(["blog_post", topic["primary_keyword"], topic["service"], topic["city_name"],
                             topic["primary_keyword"], topic["volume"], "", topic["difficulty_metric"], topic["difficulty"],
                             " | ".join(topic["secondary_keywords"]), topic["cluster_volume"],
                             " | ".join(topic["link_to"]), " | ".join(topic["flags"])])
    with (target / f"{prefix}_rejected.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["keyword", "reason"])
        writer.writerows([r["keyword"], r["reason"]] for r in result["rejected"])


def report(result: dict, target: Path, prefix: str) -> None:
    counts = result["counts"]
    print(f"\n{counts['input']} keywords in, {counts['kept']} kept, {counts['rejected']} rejected.")
    print(f"\nService x city pages ({counts['money_pages']}):")
    for page in result["money_pages"][:25]:
        difficulty = f"{page['difficulty_metric']} {page['difficulty']:.0f}" if page["difficulty"] is not None else "difficulty unchecked"
        volume = f"{page['volume']:.0f}/mo" if page["volume"] is not None else "no volume data"
        print(f"  {page['path']:45} {page['primary_keyword']}  [{volume}, {difficulty}, "
              f"+{len(page['secondary_keywords'])} secondary]" + (f"  {page['flags']}" if page["flags"] else ""))
    print(f"\nBlog topics ({counts['blog_topics']}):")
    for topic in result["blog_topics"][:15]:
        print(f"  {topic['primary_keyword']}  ->  {', '.join(topic['link_to']) or 'no money page yet'}")
    if counts["unassigned_money"]:
        print(f"\n{counts['unassigned_money']} money keywords matched no service in business.json "
              "(see 'unassigned_money_keywords' - add a service or a 'keywords' alias).")
    print(f"\nSaved {target / (prefix + '.json')}, .csv and _rejected.csv")


def build_seeds(business: dict, near_me: bool) -> list[str]:
    seeds = []
    cities = [city_name(a) for a in [business.get("primary_metro", ""), *(business.get("service_areas") or [])] if a]
    for service in business.get("services") or []:
        terms = [service["name"], *(service.get("keywords") or [])[:1]]
        for term in terms:
            for city in dict.fromkeys(cities):
                seeds.append(f"{term} {city}".lower())
            if near_me:
                seeds.append(f"{term} near me".lower())
    return list(dict.fromkeys(seeds))


def add_filter_flags(parser) -> None:
    parser.add_argument("--min-volume", type=float, default=50, help="Step 1: minimum monthly searches (default 50; use 100 in large metros).")
    parser.add_argument("--max-kd", type=float, default=30, help="Step 2: max link-based KD from an export (default 30).")
    parser.add_argument("--max-serp-difficulty", type=float, default=35, help="Step 2: max serp_difficulty (default 35 = EASY).")
    parser.add_argument("--max-comp-index", type=float, default=50, help="Step 2: max Keyword Planner competition index (default 50).")
    parser.add_argument("--min-cpc", type=float, default=0.01, help="Step 4: minimum CPC in USD for money keywords (default 0.01 = any paid competition).")
    parser.add_argument("--min-secondary", type=int, default=3)
    parser.add_argument("--max-secondary", type=int, default=5)
    parser.add_argument("--allow-unverified", action="store_true", help="Keep Trends-fallback rows, labelled, with no metrics.")
    parser.add_argument("--map-prefix", default="keyword-map")


def main(argv=None) -> int:
    utf8_stdout()
    parser = argparse.ArgumentParser(description="Local keyword research: seeds, metrics, 4-step filter, clusters.")
    parser.add_argument("--business", default=None)
    parser.add_argument("--out-dir", default=None)
    sub = parser.add_subparsers(dest="command", required=True)

    p_seeds = sub.add_parser("seeds", help="Build the service x city seed list.")
    p_seeds.add_argument("--no-near-me", action="store_true")

    p_run = sub.add_parser("run", help="Fetch metrics through the keyword engine, then filter.")
    p_run.add_argument("--prefix", default=None, help="Output prefix (default: business name slug).")
    p_run.add_argument("--provider", default="auto", choices=["auto", "apify", "trends"])
    p_run.add_argument("--max-ideas", type=int, default=100, help="Keyword rows from Apify, $0.012 each (default 100).")
    p_run.add_argument("--serp-top", type=int, default=0, help="Also check page one for the top N rows, $0.0045 each (default 0 = skip).")
    p_run.add_argument("--no-near-me", action="store_true")
    add_filter_flags(p_run)

    p_filter = sub.add_parser("filter", help="Filter and cluster an existing keyword file.")
    p_filter.add_argument("--input", required=True, help="<prefix>_verified.csv or a Semrush/Ahrefs export.")
    p_filter.add_argument("--serp", help="<prefix>_serp.csv (auto-detected next to --input).")
    add_filter_flags(p_filter)

    args = parser.parse_args(argv)
    business = load_business(args.business)
    target = out_dir(args.out_dir)

    if args.command == "seeds":
        seeds = build_seeds(business, not args.no_near_me)
        (target / "seeds.txt").write_text("\n".join(seeds) + "\n", encoding="utf-8")
        print("\n".join(seeds))
        print(f"\n{len(seeds)} seeds saved to {target / 'seeds.txt'}")
        return 0

    if args.command == "run":
        finder = keyword_finder_dir()
        if not finder:
            raise SystemExit("Keyword engine not found. Run inside the AfriShield folder or set AFRISHIELD_ROOT "
                             "to the folder holding '00 Knowledge/Keyword Finder'.")
        prefix = args.prefix or slugify(business.get("name", "local"))
        seeds = build_seeds(business, not args.no_near_me)
        seeds_file = target / "seeds.txt"
        seeds_file.write_text("\n".join(seeds) + "\n", encoding="utf-8")
        command = [sys.executable, str(finder / "keyword_orchestrator.py"), "--seeds-file", str(seeds_file),
                   "--provider", args.provider, "--save-raw", "--prefix", prefix, "--out-dir", str(target),
                   "--min-volume", str(int(args.min_volume)), "--apify-max-ideas", str(args.max_ideas)]
        if business.get("country_code"):
            command += ["--country", business["country_code"]]
        if business.get("language"):
            command += ["--lang", business["language"]]
        brands = [c.get("name") if isinstance(c, dict) else c for c in business.get("competitors") or []]
        if any(brands):
            command += ["--exclude-brands", ",".join(b for b in brands if b)]
        print(f"{len(seeds)} seeds -> keyword engine (provider {args.provider}, up to {args.max_ideas} rows, "
              f"about ${args.max_ideas * 0.012:.2f} if Apify answers)")
        if subprocess.run(command).returncode != 0:
            raise SystemExit("The keyword engine failed - see its output above.")
        verified = target / f"{prefix}_verified.csv"
        if args.serp_top:
            serp_command = [sys.executable, str(finder / "serp_competition.py"), "--input", str(verified),
                            "--top", str(args.serp_top), "--out-dir", str(target)]
            if business.get("country_code"):
                serp_command += ["--country", business["country_code"]]
            if business.get("language"):
                serp_command += ["--lang", business["language"]]
            domain = re.sub(r"^https?://(www\.)?", "", business.get("website", "")).strip("/")
            if domain:
                serp_command += ["--own-domain", domain]
            if subprocess.run(serp_command).returncode != 0:
                print("serp_competition.py failed - continuing without SERP difficulty.")
        args.input, args.serp = str(verified), None

    source = Path(args.input)
    rows = read_rows(source)
    serp_path = Path(args.serp) if args.serp else source.with_name(source.name.replace("_verified.csv", "_serp.csv"))
    if serp_path != source and serp_path.is_file():
        print(f"Merged SERP difficulty for {merge_serp(rows, serp_path)} keywords from {serp_path.name}")
    result = run_filter(rows, business, args)
    result["source"] = str(source)
    write_map(result, target, args.map_prefix)
    report(result, target, args.map_prefix)
    return 0


if __name__ == "__main__":
    sys.exit(main())
