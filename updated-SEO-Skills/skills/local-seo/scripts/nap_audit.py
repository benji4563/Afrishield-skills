#!/usr/bin/env python3
"""
nap_audit.py — check Name / Address / Phone consistency across the web.

Fetches the business website and every citation URL, then compares what each
page shows (visible text and JSON-LD) with the canonical NAP in business.json.
Also checks that the phone number carries a local area code.

Statuses
  MATCH        name, phone and address all agree
  MISMATCH     the page names the business but shows a different phone number,
               or its JSON-LD disagrees with business.json
  PARTIAL      some of the NAP is missing or written differently - compare by eye
  NOT_LISTED   the business does not appear on the page at all
  FETCH_FAILED the site blocked the request (common on Yelp, Facebook, BBB) -
               open it by hand

Finding the citation URLs is the agent's job (search "<name>" "<phone>" and
"<name>" "<city>"); list them under "citations" in business.json or pass --urls.

Usage
  python nap_audit.py
  python nap_audit.py --urls https://www.yelp.com/biz/example https://www.yellowpages.ca/bus/example
  python nap_audit.py --urls-file citations.txt
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
from pathlib import Path

from _common import BROWSER_UA, http_get, load_business, out_dir, utf8_stdout, write_json

PHONE_RE = re.compile(r"(?<![\w.])\+?\(?\d[\d\s().\-]{7,17}\d(?![\w])")
ABBREVIATIONS = {
    "street": "st", "avenue": "ave", "road": "rd", "boulevard": "blvd", "drive": "dr",
    "lane": "ln", "court": "ct", "place": "pl", "highway": "hwy", "suite": "ste",
    "north": "n", "south": "s", "east": "e", "west": "w", "and": "&",
}


def digits(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def norm(text: str) -> str:
    text = re.sub(r"[^a-z0-9&\s]", " ", (text or "").lower())
    return " ".join(ABBREVIATIONS.get(word, word) for word in text.split())


def visible_text(page: str) -> str:
    page = re.sub(r"(?is)<(script|style|noscript|svg)\b.*?</\1>", " ", page)
    return html.unescape(re.sub(r"(?s)<[^>]+>", " ", page))


def json_ld_blocks(page: str) -> list[dict]:
    found = []
    for raw in re.findall(r'(?is)<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', page):
        try:
            data = json.loads(raw.strip())
        except json.JSONDecodeError:
            continue
        stack = [data]
        while stack:
            item = stack.pop()
            if isinstance(item, list):
                stack.extend(item)
            elif isinstance(item, dict):
                found.append(item)
                stack.extend(v for v in item.values() if isinstance(v, (dict, list)))
    return found


def same_phone(a: str, b: str) -> bool:
    """Equal once formatting and a leading country code or trunk zero are ignored."""
    a, b = a.lstrip("0"), b.lstrip("0")
    if a == b:
        return True
    short, long = sorted((a, b), key=len)
    return len(short) >= 7 and long.endswith(short) and len(long) - len(short) <= 3


def phones_in(text: str) -> set[str]:
    found = set()
    for match in PHONE_RE.findall(text):
        number = digits(match)
        if 9 <= len(number) <= 15:
            found.add(number)
    return found


def area_code_check(phone: str, expected: list[str], dialing_code: str) -> tuple[str, str]:
    number = digits(phone)
    dialing_code = digits(dialing_code)
    if not number:
        return "FAIL", "No phone number in business.json."
    if not expected:
        return "SKIPPED", "Add 'expected_area_codes' to business.json to check the area code."
    national = number[len(dialing_code):] if dialing_code and number.startswith(dialing_code) else number.lstrip("0")
    for code in expected:
        if national.startswith(digits(code)):
            return "PASS", f"Area code {code} is local."
    return "FAIL", (f"{phone} does not start with a local area code ({', '.join(expected)}). "
                    "A toll-free or out-of-area number weakens local relevance.")


def audit_page(url: str, canon: dict) -> dict:
    status, page = http_get(url, headers={"User-Agent": BROWSER_UA, "Accept-Language": "en"})
    row = {"url": url, "http_status": status, "name": "", "phone": "", "address": "",
           "other_phones": "", "schema_nap": "", "status": "", "notes": ""}
    if status != 200:
        row["status"] = "FETCH_FAILED"
        row["notes"] = f"HTTP {status or 'no response'} - check this listing by hand."
        return row

    text = visible_text(page)
    flat = norm(text)
    phones = phones_in(text)

    row["name"] = "yes" if canon["name"] and canon["name"] in flat else "no"
    matching = {p for p in phones if same_phone(p, canon["phone"])}
    row["phone"] = "yes" if matching else "no"
    others = sorted(phones - matching)
    row["other_phones"] = " ".join(others[:5])

    # NAP published in JSON-LD counts as shown, and is checked for disagreement.
    schema_issues = []
    schema_text = ""
    for block in json_ld_blocks(page):
        telephone = block.get("telephone")
        if isinstance(telephone, str) and digits(telephone):
            if same_phone(digits(telephone), canon["phone"]):
                row["phone"] = "yes"
            else:
                schema_issues.append(f"telephone {telephone}")
        address = block.get("address")
        if isinstance(address, dict):
            schema_text += " " + norm(" ".join(str(v) for v in address.values() if isinstance(v, str)))
            postal = norm(str(address.get("postalCode", "")))
            if canon["postal"] and postal and postal.replace(" ", "") != canon["postal"].replace(" ", ""):
                schema_issues.append(f"postalCode {address.get('postalCode')}")
    row["schema_nap"] = "; ".join(schema_issues) or "ok"

    address_parts = [p for p in (canon["street"], canon["postal"]) if p]
    if not address_parts:
        row["address"] = "n/a"
    else:
        haystack = (flat + " " + schema_text).replace(" ", "")
        hits = [p for p in address_parts if p.replace(" ", "") in haystack]
        row["address"] = "yes" if len(hits) == len(address_parts) else ("partial" if hits else "no")

    different_phone = row["phone"] == "no" and bool(others)
    if row["name"] == "no" and row["phone"] == "no" and row["address"] in ("no", "n/a") and not schema_issues:
        row["status"] = "NOT_LISTED"
        row["notes"] = "the business does not appear on this page"
    elif schema_issues or (different_phone and row["name"] == "yes"):
        row["status"] = "MISMATCH"
        reasons = (["shows a different phone number"] if different_phone else []) \
            + (["JSON-LD disagrees"] if schema_issues else [])
        row["notes"] = "; ".join(reasons)
    elif row["name"] == "yes" and row["phone"] == "yes" and row["address"] in ("yes", "n/a"):
        row["status"] = "MATCH"
    else:
        row["status"] = "PARTIAL"
        missing = [k for k in ("name", "phone", "address") if row[k] in ("no", "partial")]
        row["notes"] = "not found as written: " + ", ".join(missing) + " - compare by eye"
    return row


def main(argv=None) -> int:
    utf8_stdout()
    parser = argparse.ArgumentParser(description="Audit NAP consistency across the website and citations.")
    parser.add_argument("--business", default=None)
    parser.add_argument("--urls", nargs="*", default=[])
    parser.add_argument("--urls-file")
    parser.add_argument("--out-dir", default=None)
    args = parser.parse_args(argv)

    business = load_business(args.business)
    address = business.get("address") or {}
    hide_address = bool(business.get("hide_address"))
    canon = {
        "name": norm(business.get("name", "")),
        "phone": digits(business.get("phone", "")),
        # A service-area business that hides its address is matched on name and phone only.
        "street": "" if hide_address else norm(address.get("street", "")),
        "postal": "" if hide_address else norm(address.get("postal_code", "")),
    }

    urls = list(args.urls)
    if args.urls_file:
        urls += [line.strip() for line in Path(args.urls_file).read_text(encoding="utf-8").splitlines()
                 if line.strip() and not line.startswith("#")]
    if not urls:
        urls = [u for u in [business.get("website"), *(business.get("citations") or [])] if u]
    urls = list(dict.fromkeys(urls))
    if not urls:
        raise SystemExit("No URLs to audit. Add 'website' and 'citations' to business.json or pass --urls.")

    area_status, area_note = area_code_check(
        business.get("phone", ""), business.get("expected_area_codes") or [],
        business.get("phone_country_code", ""))
    print(f"Canonical NAP: {business.get('name')} | {business.get('phone')} | "
          f"{'(address hidden - SAB)' if hide_address else address.get('street', '')}")
    print(f"Area code: {area_status} - {area_note}\n")

    rows = []
    for url in urls:
        row = audit_page(url, canon)
        rows.append(row)
        print(f"{row['status']:13} {url}" + (f"  ({row['notes']})" if row["notes"] else ""))

    target = out_dir(args.out_dir)
    fields = ["url", "status", "http_status", "name", "phone", "address", "other_phones", "schema_nap", "notes"]
    with (target / "nap-audit.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    counts = {s: sum(r["status"] == s for r in rows) for s in ("MATCH", "PARTIAL", "MISMATCH", "NOT_LISTED", "FETCH_FAILED")}
    write_json(target / "nap-audit.json", {"area_code": {"status": area_status, "note": area_note},
                                           "counts": counts, "pages": rows})
    print(f"\n{counts}")
    print(f"Saved {target / 'nap-audit.csv'} and nap-audit.json")
    return 1 if counts["MISMATCH"] or area_status == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
