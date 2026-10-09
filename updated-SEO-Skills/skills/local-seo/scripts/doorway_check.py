#!/usr/bin/env python3
"""
doorway_check.py — the anti-doorway gate for Service x City pages.

Reads the page data files (content/local-seo/pages/*.json) that drive the
Next.js template and refuses to pass pages that are a city-name swap of one
another. Run it before any page is set to "status": "ready".

Per-page requirements
  - definition block of 40-70 words; title <= 60 chars; meta description 50-160
  - at least 3 local landmarks, 2 cross streets, 4 neighbourhoods
  - local notes of 60+ words (housing stock, bylaws, permits, climate, access)
  - at least one verified local testimonial OR one local project history
    (testimonials must be real: "verified": true means the client supplied it)
  - at least 4 FAQs, one comparison table with a one-sentence summary,
    geo coordinates, a service radius
  - no placeholder text (TODO, {{...}}, lorem ipsum, [city])

Cross-page requirement
  Unique copy (definition, intro, local notes, FAQ answers, project summaries),
  with place names masked, is compared pairwise by 4-word shingles.
  Similarity >= --fail-at (0.50) fails both pages; >= --warn-at (0.30) warns.

Exit code 1 when any page with status "ready" fails.

Usage
  python doorway_check.py
  python doorway_check.py --pages content/local-seo/pages --all
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from itertools import combinations
from pathlib import Path

from _common import utf8_stdout

PLACEHOLDER = re.compile(r"\bTODO\b|\{\{|\}\}|lorem ipsum|\bXXX+\b|\[city\]|\[service\]", re.I)
DEFAULT_PAGES = Path("content") / "local-seo" / "pages"


def words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", (text or "").lower())


def all_strings(value) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [s for v in value.values() for s in all_strings(v)]
    if isinstance(value, list):
        return [s for v in value for s in all_strings(v)]
    return []


def place_names(page: dict) -> list[str]:
    local = page.get("local") or {}
    names = [page.get("cityName", ""), page.get("city", "").replace("-", " ")]
    names += local.get("neighborhoods") or []
    names += [l.get("name", "") if isinstance(l, dict) else str(l) for l in local.get("landmarks") or []]
    names += local.get("crossStreets") or []
    return sorted({n.lower() for n in names if n and len(n) > 2}, key=len, reverse=True)


def unique_copy(page: dict) -> str:
    local = page.get("local") or {}
    parts = [page.get("definition", ""), page.get("intro", ""), local.get("localNotes", "")]
    parts += [f.get("a", "") for f in page.get("faqs") or []]
    parts += [p.get("summary", "") for p in page.get("projects") or []]
    text = " ".join(parts).lower()
    for name in place_names(page):
        text = text.replace(name, " _place_ ")
    return text


def shingles(text: str, size: int = 4) -> set[tuple[str, ...]]:
    tokens = words(text)
    return {tuple(tokens[i:i + size]) for i in range(len(tokens) - size + 1)}


def check_page(page: dict) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    local = page.get("local") or {}

    for field in ("service", "city", "cityName", "serviceName", "primaryKeyword", "h1", "title", "metaDescription",
                  "definition", "intro"):
        if not str(page.get(field) or "").strip():
            errors.append(f"missing '{field}'")

    title, meta = page.get("title", ""), page.get("metaDescription", "")
    if len(title) > 60:
        warnings.append(f"title is {len(title)} chars (aim for 60 or fewer)")
    if meta and not 50 <= len(meta) <= 160:
        warnings.append(f"meta description is {len(meta)} chars (aim for 50-160)")
    city = (page.get("cityName") or "").lower()
    if city and city not in (page.get("h1") or "").lower():
        errors.append("h1 does not name the city")

    definition_words = len(words(page.get("definition", "")))
    if definition_words and not 40 <= definition_words <= 70:
        errors.append(f"definition block is {definition_words} words (must be 40-70)")

    for field, minimum, label in (("landmarks", 3, "local landmarks"), ("crossStreets", 2, "cross streets"),
                                  ("neighborhoods", 4, "neighbourhoods")):
        count = len(local.get(field) or [])
        if count < minimum:
            errors.append(f"{count} {label} (need {minimum}+)")
    for landmark in local.get("landmarks") or []:
        if isinstance(landmark, dict) and not (landmark.get("context") or "").strip():
            warnings.append(f"landmark '{landmark.get('name')}' has no context sentence - a bare name is filler")
    notes_words = len(words(local.get("localNotes", "")))
    if notes_words < 60:
        errors.append(f"local notes are {notes_words} words (need 60+ on what is specific to this area)")

    testimonials = page.get("testimonials") or []
    verified = [t for t in testimonials if t.get("verified") is True and (t.get("quote") or "").strip()]
    unverified = [t for t in testimonials if t.get("verified") is not True]
    projects = [p for p in page.get("projects") or [] if (p.get("summary") or "").strip()]
    if unverified:
        errors.append(f"{len(unverified)} testimonial(s) not marked verified - remove them or get the real quote; "
                      "never write a testimonial")
    if not verified and not projects:
        errors.append("no verified local testimonial and no local project history - the page has no local proof")
    elif not verified:
        warnings.append("no local testimonial yet (project history only)")
    for project in projects:
        if len(words(project.get("summary", ""))) < 25:
            warnings.append(f"project '{project.get('title')}' summary is thin (under 25 words)")

    faqs = page.get("faqs") or []
    if len(faqs) < 4:
        errors.append(f"{len(faqs)} FAQs (need 4+)")
    if not any(city and city in (f.get("q", "") + f.get("a", "")).lower() for f in faqs):
        warnings.append("no FAQ mentions the city - at least one should answer a local question")
    comparison = page.get("comparison") or {}
    if not (comparison.get("columns") and comparison.get("rows")):
        errors.append("no comparison table")
    elif len(words(comparison.get("summary", ""))) < 12:
        errors.append("comparison table needs a 'summary' sentence (12+ words) stating its takeaway")

    geo = page.get("geo") or {}
    if not isinstance(geo.get("lat"), (int, float)) or not isinstance(geo.get("lng"), (int, float)):
        errors.append("missing geo coordinates (lat/lng) - take them from service-areas.json")
    if not page.get("serviceRadiusKm"):
        errors.append("missing serviceRadiusKm")

    hits = sorted({m.group(0) for s in all_strings(page) for m in PLACEHOLDER.finditer(s)})
    if hits:
        errors.append(f"placeholder text: {', '.join(hits)}")
    return errors, warnings


def main(argv=None) -> int:
    utf8_stdout()
    parser = argparse.ArgumentParser(description="Anti-doorway gate for Service x City page data.")
    parser.add_argument("--pages", default=str(DEFAULT_PAGES), help="Folder of page JSON files.")
    parser.add_argument("--all", action="store_true", help="Fail on drafts too, not only pages marked ready.")
    parser.add_argument("--fail-at", type=float, default=0.50)
    parser.add_argument("--warn-at", type=float, default=0.30)
    args = parser.parse_args(argv)

    folder = Path(args.pages)
    # Files starting with "_" are examples: the template never builds them either.
    files = sorted(p for p in folder.glob("*.json") if not p.name.startswith("_"))
    if not files:
        raise SystemExit(f"No page files in {folder} (files starting with '_' are examples and are skipped).")

    pages = []
    for path in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            print(f"FAIL  {path.name}: invalid JSON ({error})")
            return 1
        errors, warnings = check_page(data)
        expected = f"{data.get('service')}--{data.get('city')}.json"
        if path.name != expected:
            warnings.append(f"file should be named {expected}")
        pages.append({"file": path.name, "data": data, "errors": errors, "warnings": warnings,
                      "shingles": shingles(unique_copy(data))})

    for a, b in combinations(pages, 2):
        if not a["shingles"] or not b["shingles"]:
            continue
        similarity = len(a["shingles"] & b["shingles"]) / len(a["shingles"] | b["shingles"])
        if similarity >= args.fail_at:
            for page, other in ((a, b), (b, a)):
                # A published page is not at fault for a draft that copies it.
                copied_by_draft = page["data"].get("status") == "ready" and other["data"].get("status") != "ready"
                page["warnings" if copied_by_draft else "errors"].append(
                    f"{similarity:.0%} of unique copy matches {other['file']} - doorway risk, rewrite")
        elif similarity >= args.warn_at:
            for page, other in ((a, b), (b, a)):
                page["warnings"].append(f"{similarity:.0%} of unique copy overlaps {other['file']}")

    failed = 0
    for page in pages:
        status = page["data"].get("status", "draft")
        gated = status == "ready" or args.all
        verdict = "PASS" if not page["errors"] else ("FAIL" if gated else "DRAFT")
        failed += verdict == "FAIL"
        print(f"{verdict:5} {page['file']}  [status: {status}]")
        for error in page["errors"]:
            print(f"        x {error}")
        for warning in page["warnings"]:
            print(f"        ! {warning}")

    ready = sum(p["data"].get("status") == "ready" for p in pages)
    print(f"\n{len(pages)} pages checked, {ready} marked ready, {failed} failing.")
    if failed:
        print("Fix the failures or set those pages back to \"status\": \"draft\" - the template only builds ready pages.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
