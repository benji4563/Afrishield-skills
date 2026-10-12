#!/usr/bin/env python3
"""
geo_audit.py — technical, on-page and GEO (generative engine) audit.

Checks the raw server HTML, which is what AI crawlers read (most do not run
JavaScript), so it works against a local dev server as well as the live site.

Per page
  Technical  HTTP 200, canonical, viewport, lang, no stray noindex
  On-page    title (<= 60), meta description (50-160), exactly one H1, image alt text
  Schema     every JSON-LD block parses; LocalBusiness and Service carry the
             fields that matter; FAQPage questions are visible on the page
  GEO        a citable definition block in the first two paragraphs after the H1
             (40-70 words); H2 sections
             that open with a direct answer; lists or tables; body copy present
             without JavaScript
  Links      blog pages link to at least one service page

Site level
  robots.txt reachable, AI crawlers not blocked, sitemap declared;
  sitemap.xml parses, lists same-host URLs, and those URLs return 200.

Lighthouse (--psi)
  Runs Google PageSpeed Insights (mobile) and checks the four category scores
  against --min-score (90) plus LCP, CLS and INP. PSI_API_KEY is optional but
  avoids the shared anonymous quota. A local Lighthouse JSON report can be
  checked instead with --lighthouse-json.

Exit code 1 when any check fails.

Usage
  python geo_audit.py --url http://localhost:3000/services/drain-cleaning/etobicoke
  python geo_audit.py --site https://example.com --max-pages 25
  python geo_audit.py --site https://example.com --psi
  python geo_audit.py --lighthouse-json lighthouse-report.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

from _common import BROWSER_UA, http_get, load_env, out_dir, utf8_stdout, write_json

AI_CRAWLERS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot",
               "PerplexityBot", "Google-Extended"]
LOCAL_TYPES = {"LocalBusiness", "ProfessionalService", "HomeAndConstructionBusiness", "Plumber", "Electrician",
               "HVACBusiness", "RoofingContractor", "GeneralContractor", "AccountingService", "LegalService",
               "Dentist", "MedicalBusiness", "AutoRepair", "Locksmith", "MovingCompany", "HousePainter"}
PSI = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
VOID = {"br", "img", "hr", "meta", "link", "input", "source", "area", "base", "col", "embed", "track", "wbr"}
SKIP = {"script", "style", "noscript", "svg", "template"}
BLOCKS = {"p", "h1", "h2", "h3", "li", "td", "th"}


class Page(HTMLParser):
    """Collects the handful of facts the audit needs in one pass."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.meta: dict[str, str] = {}
        self.canonical = ""
        self.lang = ""
        self.links: list[str] = []
        self.images = self.images_without_alt = 0
        self.tables = self.lists = 0
        self.json_ld: list[str] = []
        self.blocks: list[tuple[str, str]] = []   # (tag, text) in document order
        self.text_parts: list[str] = []
        self._skip = 0
        self._capture: list[tuple[str, list[str]]] = []
        self._in_title = False
        self._ld = None

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if tag == "script" and a.get("type", "").lower() == "application/ld+json":
            self._ld = []
        if tag in SKIP:
            self._skip += 1
            return
        if tag == "html":
            self.lang = a.get("lang", "")
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            key = (a.get("name") or a.get("property") or "").lower()
            if key:
                self.meta[key] = a.get("content", "")
        elif tag == "link" and "canonical" in a.get("rel", "").lower():
            self.canonical = a.get("href", "")
        elif tag == "a" and a.get("href"):
            self.links.append(a["href"])
        elif tag == "img":
            self.images += 1
            if not a.get("alt", "").strip() and a.get("role") != "presentation" and a.get("aria-hidden") != "true":
                self.images_without_alt += 1
        elif tag == "table":
            self.tables += 1
        elif tag in ("ul", "ol"):
            self.lists += 1
        if tag in BLOCKS:
            self._capture.append((tag, []))

    def handle_endtag(self, tag):
        if tag in SKIP:
            self._skip = max(0, self._skip - 1)
            if tag == "script" and self._ld is not None:
                self.json_ld.append("".join(self._ld))
                self._ld = None
            return
        if tag == "title":
            self._in_title = False
        if tag in BLOCKS:
            for index in range(len(self._capture) - 1, -1, -1):
                if self._capture[index][0] == tag:
                    text = " ".join("".join(self._capture[index][1]).split())
                    if text:
                        self.blocks.append((tag, text))
                    del self._capture[index:]
                    break

    def handle_data(self, data):
        if self._ld is not None:
            self._ld.append(data)
            return
        if self._skip:
            return
        if self._in_title:
            self.title += data
        self.text_parts.append(data)
        for _, parts in self._capture:
            parts.append(data)


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9']+", text))


def schema_items(blocks: list[str]) -> tuple[list[dict], int]:
    items, broken = [], 0
    for raw in blocks:
        try:
            data = json.loads(raw.strip())
        except json.JSONDecodeError:
            broken += 1
            continue
        stack = [data]
        while stack:
            node = stack.pop()
            if isinstance(node, list):
                stack.extend(node)
            elif isinstance(node, dict):
                if "@type" in node:
                    items.append(node)
                stack.extend(v for v in node.values() if isinstance(v, (dict, list)))
    return items, broken


def types_of(item: dict) -> set[str]:
    kind = item.get("@type")
    return set(kind) if isinstance(kind, list) else {kind}


def money_matcher(prefixes: list[str] | None):
    """Return a test for 'is this path a money page'.

    With no configured prefixes the suite's own layout applies (/services/...,
    /locations/...). A site built differently lists its money-page paths in
    business.json (`money_page_paths`) or passes --money-path.
    """
    cleaned = ["/" + p.strip().strip("/") for p in (prefixes or []) if p and p.strip().strip("/")]
    if not cleaned:
        return (lambda path: bool(re.match(r"^/(services|locations)/[^/]+", path))), "/services/..."

    def test(path: str) -> bool:
        bare = path.rstrip("/") or "/"
        return any(bare == prefix or bare.startswith(prefix + "/") for prefix in cleaned)

    return test, ", ".join(cleaned)


def configured_money_paths(cli: list[str] | None) -> list[str] | None:
    if cli:
        return cli
    business = Path("local-seo") / "business.json"
    if business.is_file():
        try:
            paths = json.loads(business.read_text(encoding="utf-8")).get("money_page_paths")
        except (OSError, ValueError):
            return None
        if isinstance(paths, list) and paths:
            return [str(p) for p in paths]
    return None


def audit_page(url: str, html_text: str, status: int, money_paths: list[str] | None = None) -> dict:
    checks: list[dict] = []

    def add(area, name, state, detail=""):
        checks.append({"area": area, "check": name, "status": state, "detail": detail})

    if status != 200:
        add("technical", "HTTP status", "FAIL", f"HTTP {status or 'no response'}")
        return {"url": url, "checks": checks}
    add("technical", "HTTP status", "PASS", "200")

    page = Page()
    page.feed(html_text)
    path = urllib.parse.urlparse(url).path or "/"
    text = " ".join(" ".join(page.text_parts).split())
    words = word_count(text)

    robots = page.meta.get("robots", "").lower()
    add("technical", "indexable", "FAIL" if "noindex" in robots else "PASS", robots or "no robots meta")
    add("technical", "canonical", "PASS" if page.canonical else "FAIL", page.canonical or "missing")
    add("technical", "viewport", "PASS" if page.meta.get("viewport") else "FAIL", "")
    add("technical", "html lang", "PASS" if page.lang else "WARN", page.lang or "missing")

    title = " ".join(page.title.split())
    add("on-page", "title", "FAIL" if not title else ("WARN" if len(title) > 60 else "PASS"),
        f"{len(title)} chars: {title[:70]}")
    description = page.meta.get("description", "")
    add("on-page", "meta description",
        "FAIL" if not description else ("PASS" if 50 <= len(description) <= 160 else "WARN"),
        f"{len(description)} chars")
    h1s = [t for tag, t in page.blocks if tag == "h1"]
    add("on-page", "one H1", "PASS" if len(h1s) == 1 else "FAIL", f"{len(h1s)} found" + (f": {h1s[0][:70]}" if h1s else ""))
    add("on-page", "image alt text", "PASS" if not page.images_without_alt else "WARN",
        f"{page.images_without_alt} of {page.images} images lack alt text")

    items, broken = schema_items(page.json_ld)
    found = sorted({t for item in items for t in types_of(item) if t})
    add("schema", "JSON-LD parses", "FAIL" if broken else ("PASS" if items else "FAIL"),
        f"{broken} broken block(s)" if broken else (", ".join(found) or "no JSON-LD on the page"))
    for item in items:
        kinds = types_of(item)
        if "@id" in item and len(item) <= 3:
            continue  # a reference to a node defined elsewhere, e.g. Service.provider
        if kinds & LOCAL_TYPES:
            missing = [f for f in ("name", "url") if not item.get(f)]
            if not (item.get("telephone") or item.get("address")):
                missing.append("telephone or address")
            if not item.get("areaServed"):
                missing.append("areaServed")
            geo = item.get("geo") or {}
            if not (isinstance(geo, dict) and geo.get("latitude") is not None and geo.get("longitude") is not None):
                missing.append("geo coordinates")
            add("schema", "LocalBusiness fields", "FAIL" if missing else "PASS", "missing: " + ", ".join(missing) if missing else "")
        if "Service" in kinds:
            missing = [f for f in ("name", "provider", "areaServed") if not item.get(f)]
            add("schema", "Service fields", "FAIL" if missing else "PASS", "missing: " + ", ".join(missing) if missing else "")
        if "FAQPage" in kinds:
            entities = item.get("mainEntity") or []
            entities = entities if isinstance(entities, list) else [entities]
            flat = text.lower()
            empty = hidden = 0
            for entity in entities:
                question = " ".join(str(entity.get("name", "")).split())
                answer = (entity.get("acceptedAnswer") or {}).get("text", "")
                empty += not (question and str(answer).strip())
                hidden += bool(question) and question.lower() not in flat
            state = "FAIL" if (not entities or empty or hidden) else "PASS"
            add("schema", "FAQPage verified", state,
                f"{len(entities)} questions, {empty} incomplete, {hidden} not visible on the page")

    add("geo", "content without JavaScript", "PASS" if words >= 300 else "FAIL", f"{words} words in the server HTML")
    # The definition block is the first paragraph after the H1, or the one right
    # after it: many layouts put a short hero line under the heading and the
    # citable summary ("In short", "TL;DR") directly below. Labels under eight
    # words are skipped, and nothing past the first H2 counts.
    lead: list[str] = []
    seen_h1 = False
    for tag, block in page.blocks:
        if tag == "h1":
            seen_h1 = True
        elif seen_h1 and tag == "h2":
            break
        elif seen_h1 and tag == "p" and word_count(block) >= 8:
            lead.append(block)
            if len(lead) == 2:
                break
    if not lead:
        add("geo", "definition block", "FAIL", "no paragraph between the H1 and the first H2")
    else:
        counts = [word_count(block) for block in lead]
        hit = next((c for c in counts if 40 <= c <= 70), None)
        add("geo", "definition block", "PASS" if hit else "WARN",
            f"{hit or counts[0]} words (target 40-70, plain facts, no marketing adjectives)"
            + ("" if hit else " - checked the first two paragraphs after the H1"))

    sections = direct = 0
    for index, (tag, _) in enumerate(page.blocks):
        if tag != "h2":
            continue
        sections += 1
        following = next((b for b in page.blocks[index + 1:index + 4] if b[0] in ("p", "h2")), None)
        if following and following[0] == "p" and 12 <= word_count(following[1]) <= 80:
            direct += 1
    if sections:
        add("geo", "sections open with a direct answer", "PASS" if direct / sections >= 0.6 else "WARN",
            f"{direct} of {sections} H2 sections start with a 12-80 word paragraph")
    add("geo", "lists or tables", "PASS" if (page.tables or page.lists) else "WARN",
        f"{page.tables} tables, {page.lists} lists")
    is_money_path, money_label = money_matcher(money_paths)
    is_money = is_money_path(path) if money_paths else ("/services/" in path or "/locations/" in path)
    if is_money:
        add("geo", "comparison table", "PASS" if page.tables else "WARN", f"{page.tables} tables")
        add("schema", "FAQPage present", "PASS" if "FAQPage" in found else "FAIL", "")
        add("on-page", "click-to-call link", "PASS" if any(l.startswith("tel:") for l in page.links) else "FAIL", "")

    if "/blog/" in path:
        internal = [urllib.parse.urlparse(urllib.parse.urljoin(url, l)).path for l in page.links]
        money = sorted({p for p in internal if is_money_path(p)})
        add("links", "blog links to a service page", "PASS" if money else "FAIL",
            ", ".join(money[:4]) or f"no link to {money_label} - this post passes no equity to a money page")

    return {"url": url, "checks": checks}


def robots_blocks(robots: str, agent: str) -> bool:
    """True when the group for `agent` (or * when it has no group) disallows the whole site."""
    groups: dict[str, list[str]] = {}
    current: list[str] = []
    previous_was_agent = False
    for line in robots.splitlines():
        line = line.split("#")[0].strip()
        if ":" not in line:
            continue
        key, value = (part.strip() for part in line.split(":", 1))
        key = key.lower()
        if key == "user-agent":
            if not previous_was_agent:
                current = []
            groups[value.lower()] = current
            previous_was_agent = True
        else:
            previous_was_agent = False
            if key in ("allow", "disallow"):
                current.append(f"{key}:{value}")
    rules = groups.get(agent.lower(), groups.get("*", []))
    return "disallow:/" in rules and "allow:/" not in rules


def audit_site(site: str, max_pages: int) -> tuple[list[dict], list[str]]:
    checks: list[dict] = []
    root = site.rstrip("/")
    host = urllib.parse.urlparse(root).netloc

    status, robots = http_get(root + "/robots.txt")
    if status != 200:
        checks.append({"area": "site", "check": "robots.txt", "status": "FAIL", "detail": f"HTTP {status}"})
        robots = ""
    else:
        blocked = [a for a in AI_CRAWLERS if robots_blocks(robots, a)]
        checks.append({"area": "site", "check": "AI crawlers allowed", "status": "FAIL" if blocked else "PASS",
                       "detail": "blocked: " + ", ".join(blocked) if blocked else ", ".join(AI_CRAWLERS)})
        named = [a for a in AI_CRAWLERS if re.search(rf"(?im)^user-agent:\s*{re.escape(a)}\s*$", robots)]
        checks.append({"area": "site", "check": "AI crawlers named explicitly",
                       "status": "PASS" if len(named) >= 4 else "WARN", "detail": f"{len(named)} of {len(AI_CRAWLERS)} named"})
    declared = re.findall(r"(?im)^sitemap:\s*(\S+)", robots)
    checks.append({"area": "site", "check": "sitemap declared in robots.txt",
                   "status": "PASS" if declared else "WARN", "detail": ", ".join(declared)})

    sitemap_url = declared[0] if declared else root + "/sitemap.xml"
    status, body = http_get(sitemap_url)
    urls: list[str] = []
    if status != 200:
        checks.append({"area": "site", "check": "sitemap.xml", "status": "FAIL", "detail": f"{sitemap_url} -> HTTP {status}"})
    else:
        try:
            tree = ET.fromstring(body.encode("utf-8"))
            locs = [e.text.strip() for e in tree.iter() if e.tag.endswith("loc") and e.text]
            if tree.tag.endswith("sitemapindex"):
                for child in locs[:5]:
                    child_status, child_body = http_get(child)
                    if child_status == 200:
                        urls += [e.text.strip() for e in ET.fromstring(child_body.encode("utf-8")).iter()
                                 if e.tag.endswith("loc") and e.text]
            else:
                urls = locs
            foreign = [u for u in urls if urllib.parse.urlparse(u).netloc != host]
            checks.append({"area": "site", "check": "sitemap.xml",
                           "status": "FAIL" if (not urls or foreign) else "PASS",
                           "detail": f"{len(urls)} URLs" + (f", {len(foreign)} on another host (e.g. {foreign[0]})" if foreign else "")})
        except ET.ParseError as error:
            checks.append({"area": "site", "check": "sitemap.xml", "status": "FAIL", "detail": f"invalid XML: {error}"})
    return checks, urls[:max_pages]


def lighthouse_checks(report: dict, min_score: int) -> list[dict]:
    checks = []
    for key, label in (("performance", "Performance"), ("accessibility", "Accessibility"),
                       ("best-practices", "Best Practices"), ("seo", "SEO")):
        score = (report.get("categories", {}).get(key) or {}).get("score")
        if score is None:
            continue
        value = round(score * 100)
        checks.append({"area": "lighthouse", "check": label, "status": "PASS" if value >= min_score else "FAIL",
                       "detail": f"{value} (target {min_score}+)"})
    audits = report.get("audits", {})
    for key, label, limit, unit in (("largest-contentful-paint", "LCP", 2500, "ms"),
                                    ("cumulative-layout-shift", "CLS", 0.1, ""),
                                    ("interaction-to-next-paint", "INP", 200, "ms"),
                                    ("total-blocking-time", "TBT (lab stand-in for INP)", 200, "ms")):
        value = (audits.get(key) or {}).get("numericValue")
        if value is None:
            continue
        shown = f"{value:.3f}" if not unit else f"{value:.0f} {unit}"
        checks.append({"area": "lighthouse", "check": label, "status": "PASS" if value <= limit else "FAIL",
                       "detail": f"{shown} (limit {limit}{' ' + unit if unit else ''})"})
    return checks


def run_psi(url: str, min_score: int) -> list[dict]:
    query = [("url", url), ("strategy", "mobile")] + [("category", c) for c in
                                                       ("PERFORMANCE", "ACCESSIBILITY", "BEST_PRACTICES", "SEO")]
    if os.environ.get("PSI_API_KEY"):
        query.append(("key", os.environ["PSI_API_KEY"]))
    status, body = http_get(f"{PSI}?{urllib.parse.urlencode(query)}", timeout=120)
    if status != 200:
        return [{"area": "lighthouse", "check": "PageSpeed Insights", "status": "WARN",
                 "detail": f"HTTP {status} - not measured. Set PSI_API_KEY, or run `npx lighthouse {url} "
                           "--output=json --output-path=lighthouse-report.json` and pass --lighthouse-json."}]
    return lighthouse_checks(json.loads(body).get("lighthouseResult", {}), min_score)


def main(argv=None) -> int:
    utf8_stdout()
    parser = argparse.ArgumentParser(description="Technical, on-page and GEO audit of server-rendered HTML.")
    parser.add_argument("--url", nargs="*", default=[], help="Page URL(s) to audit.")
    parser.add_argument("--site", help="Site root: audits robots.txt, sitemap.xml and the pages it lists.")
    parser.add_argument("--max-pages", type=int, default=25)
    parser.add_argument("--psi", action="store_true", help="Run PageSpeed Insights on the first page (public URLs only).")
    parser.add_argument("--lighthouse-json", help="Check a saved Lighthouse JSON report instead.")
    parser.add_argument("--min-score", type=int, default=90)
    parser.add_argument("--money-path", action="append", default=[],
                        help="Path prefix of a money page, e.g. pricing or /pricing (omit the leading slash in "
                             "Git Bash, which rewrites it into a Windows path). Repeatable. Overrides "
                             "money_page_paths in local-seo/business.json; default /services, /locations.")
    parser.add_argument("--out-dir", default=None)
    args = parser.parse_args(argv)
    if not (args.url or args.site or args.lighthouse_json):
        parser.error("give --url, --site or --lighthouse-json")
    load_env()

    money_paths = configured_money_paths(args.money_path)
    site_checks, urls = [], list(args.url)
    if args.site:
        site_checks, listed = audit_site(args.site, args.max_pages)
        urls += [u for u in listed if u not in urls] or ([args.site] if not urls else [])

    pages = []
    for url in urls:
        status, body = http_get(url, headers={"User-Agent": BROWSER_UA})
        pages.append(audit_page(url, body, status, money_paths))

    lighthouse = []
    if args.lighthouse_json:
        lighthouse = lighthouse_checks(json.loads(Path(args.lighthouse_json).read_text(encoding="utf-8")), args.min_score)
    elif args.psi and urls:
        print(f"Running PageSpeed Insights on {urls[0]} (up to two minutes)...")
        lighthouse = run_psi(urls[0], args.min_score)

    lines = ["# SEO + GEO audit", ""]
    totals = {"PASS": 0, "WARN": 0, "FAIL": 0}

    def section(title: str, checks: list[dict]) -> None:
        if not checks:
            return
        lines.extend([f"## {title}", "", "| Area | Check | Status | Detail |", "|---|---|---|---|"])
        print(f"\n{title}")
        for c in checks:
            totals[c["status"]] += 1
            lines.append(f"| {c['area']} | {c['check']} | {c['status']} | {c['detail'].replace('|', '/')} |")
            if c["status"] != "PASS":
                print(f"  {c['status']:4} {c['check']}: {c['detail']}")
        if all(c["status"] == "PASS" for c in checks):
            print("  all checks pass")
        lines.append("")

    section("Site", site_checks)
    section("Lighthouse", lighthouse)
    for page in pages:
        section(page["url"], page["checks"])

    lines.insert(2, f"**{totals['PASS']} pass, {totals['WARN']} warn, {totals['FAIL']} fail** across {len(pages)} page(s).\n")
    target = out_dir(args.out_dir)
    (target / "seo-geo-audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_json(target / "seo-geo-audit.json", {"totals": totals, "site": site_checks, "lighthouse": lighthouse, "pages": pages})
    print(f"\n{totals['PASS']} pass, {totals['WARN']} warn, {totals['FAIL']} fail. "
          f"Report: {target / 'seo-geo-audit.md'}")
    return 1 if totals["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
