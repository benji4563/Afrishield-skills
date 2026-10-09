#!/usr/bin/env python3
"""
gbp_posts.py — plan, validate and dispatch a month of Google Business Profile posts.

Subcommands
  plan      Write the schedule skeleton: 2-3 slots a week for 4 weeks (8-12
            posts), rotating the content mix. The agent then fills in the copy.
  validate  Check the drafts against Google's post rules before anything is sent.
  send      POST each validated post to the Make.com webhook that publishes to
            the profile. Dry run unless --send is given.

Content mix (rotated by `plan`)
  service_highlight  a service with a local case study     topicType STANDARD
  offer              limited-time or seasonal offer        topicType OFFER
  tip                educational tip                       topicType STANDARD
  local_news         local business or community news      topicType STANDARD

Webhook: MAKE_GBP_POST_WEBHOOK_URL (environment or project .env). The payload
mirrors the Business Profile localPosts resource, so the Make "Create a Post"
module maps field for field. See references/gbp-posts.md.

Usage
  python gbp_posts.py plan --start 2026-11-02 --per-week 3
  python gbp_posts.py validate
  python gbp_posts.py send                 # dry run: prints what would be sent
  python gbp_posts.py send --send          # really dispatch
  python gbp_posts.py send --send --only post-03
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

from _common import DEFAULT_OUT, http_post_json, load_business, load_env, out_dir, utf8_stdout, write_json

MIX = ["service_highlight", "tip", "offer", "service_highlight", "local_news", "tip"]
TOPIC_TYPE = {"service_highlight": "STANDARD", "tip": "STANDARD", "local_news": "STANDARD", "offer": "OFFER"}
CTA_TYPES = {"BOOK", "ORDER", "SHOP", "LEARN_MORE", "SIGN_UP", "CALL"}
WEEKDAYS = {2: [1, 3], 3: [0, 2, 4]}  # Tue/Thu or Mon/Wed/Fri
MAX_SUMMARY, IDEAL_MIN, MAX_OFFER_TITLE = 1500, 80, 58
PHONE = re.compile(r"\+?\(?\d[\d\s().\-]{7,}\d")
DEFAULT_FILE = DEFAULT_OUT / "gbp-posts.json"


def plan(args) -> int:
    business = load_business(args.business)
    start = date.fromisoformat(args.start) if args.start else date.today() + timedelta(days=1)
    start -= timedelta(days=start.weekday())  # back to Monday
    if start <= date.today():
        start += timedelta(days=7)
    services = [s["name"] for s in business.get("services") or []] or ["(service)"]
    website = business.get("website", "")
    posts = []
    for week in range(args.weeks):
        for weekday in WEEKDAYS[args.per_week]:
            index = len(posts)
            kind = MIX[index % len(MIX)]
            day = start + timedelta(weeks=week, days=weekday)
            post = {
                "id": f"post-{index + 1:02d}",
                "scheduled_for": f"{day.isoformat()}T{args.time}:00",
                "timezone": business.get("timezone", ""),
                "content_type": kind,
                "topicType": TOPIC_TYPE[kind],
                "focus_service": services[index % len(services)] if kind != "local_news" else "",
                "target_keyword": "",
                "summary": "",
                "callToAction": {"actionType": "LEARN_MORE", "url": website},
                "media": [{"mediaFormat": "PHOTO", "sourceUrl": ""}],
                "status": "draft",
            }
            if kind == "offer":
                post["offer"] = {"title": "", "couponCode": "", "redeemOnlineUrl": website, "termsConditions": "",
                                 "startDate": day.isoformat(), "endDate": (day + timedelta(days=14)).isoformat()}
            posts.append(post)
    target = Path(args.file)
    if target.exists() and not args.force:
        raise SystemExit(f"{target} already exists. Pass --force to overwrite it.")
    out_dir(target.parent)
    write_json(target, {"business": business.get("name", ""), "languageCode": business.get("language", "en"),
                        "posts": posts})
    print(f"{len(posts)} post slots from {posts[0]['scheduled_for'][:10]} to {posts[-1]['scheduled_for'][:10]} -> {target}")
    for post in posts:
        print(f"  {post['id']}  {post['scheduled_for']}  {post['content_type']:18} {post['focus_service']}")
    return 0


def check(posts: list[dict]) -> tuple[dict[str, list[str]], dict[str, list[str]], list[str]]:
    errors: dict[str, list[str]] = {}
    warnings: dict[str, list[str]] = {}
    general = []
    for post in posts:
        err, warn = [], []
        summary = (post.get("summary") or "").strip()
        if not summary:
            err.append("empty summary")
        if len(summary) > MAX_SUMMARY:
            err.append(f"summary is {len(summary)} chars (Google's limit is {MAX_SUMMARY})")
        elif summary and len(summary) < IDEAL_MIN:
            warn.append(f"summary is only {len(summary)} chars - too thin to carry a keyword and a reason to act")
        if any(sum(c.isdigit() for c in m) >= 10 for m in PHONE.findall(summary)):  # 10+ digits: not a date
            err.append("summary contains a phone number - Google rejects posts with phone numbers; use the CALL button")
        if re.search(r"\{\{|\bTODO\b|lorem ipsum", summary, re.I):
            err.append("placeholder text in summary")
        if post.get("topicType") not in ("STANDARD", "OFFER", "EVENT"):
            err.append(f"topicType '{post.get('topicType')}' is not STANDARD, OFFER or EVENT")
        cta = post.get("callToAction") or {}
        if cta:
            if cta.get("actionType") not in CTA_TYPES:
                err.append(f"callToAction.actionType '{cta.get('actionType')}' not one of {sorted(CTA_TYPES)}")
            elif cta["actionType"] != "CALL" and not str(cta.get("url", "")).startswith("https://"):
                err.append("callToAction.url must be an https:// link")
        media = [m for m in post.get("media") or [] if m.get("sourceUrl")]
        if not media:
            warn.append("no photo - posts with an image get more views")
        for item in media:
            if not item["sourceUrl"].startswith("https://"):
                err.append("media sourceUrl must be a public https:// URL")
        if post.get("topicType") == "OFFER":
            offer = post.get("offer") or {}
            title = offer.get("title", "")
            if not title:
                err.append("offer needs a title")
            elif len(title) > MAX_OFFER_TITLE:
                err.append(f"offer title is {len(title)} chars (limit {MAX_OFFER_TITLE})")
            try:
                if date.fromisoformat(offer.get("endDate", "")) < date.fromisoformat(offer.get("startDate", "")):
                    err.append("offer ends before it starts")
            except ValueError:
                err.append("offer needs startDate and endDate (YYYY-MM-DD)")
            if not offer.get("termsConditions"):
                warn.append("offer has no terms and conditions")
        try:
            when = datetime.fromisoformat(post.get("scheduled_for", ""))
            if when < datetime.now():
                warn.append("scheduled time is in the past")
        except ValueError:
            err.append("scheduled_for is not an ISO date-time")
        if err:
            errors[post.get("id", "?")] = err
        if warn:
            warnings[post.get("id", "?")] = warn

    if not 8 <= len(posts) <= 12:
        general.append(f"{len(posts)} posts - a month should hold 8 to 12")
    per_week = Counter()
    for post in posts:
        try:
            per_week[datetime.fromisoformat(post["scheduled_for"]).isocalendar()[:2]] += 1
        except (ValueError, KeyError):
            pass
    off = {f"{y}-W{w:02d}": n for (y, w), n in per_week.items() if not 2 <= n <= 3}
    if off:
        general.append(f"weeks outside the 2-3 posts cadence: {off}")
    kinds = Counter(p.get("content_type") for p in posts)
    for kind in ("service_highlight", "offer", "tip", "local_news"):
        if not kinds.get(kind):
            general.append(f"no '{kind}' post in the month")
    openers = Counter(" ".join((p.get("summary") or "").lower().split()[:5]) for p in posts if p.get("summary"))
    repeated = [o for o, n in openers.items() if n > 1]
    if repeated:
        general.append(f"posts open with the same words: {repeated}")
    return errors, warnings, general


def load_posts(path: str) -> dict:
    target = Path(path)
    if not target.is_file():
        raise SystemExit(f"{target} not found. Run `gbp_posts.py plan` first.")
    return json.loads(target.read_text(encoding="utf-8"))


def validate(args) -> int:
    data = load_posts(args.file)
    errors, warnings, general = check(data["posts"])
    for post in data["posts"]:
        pid = post.get("id", "?")
        print(f"{'FAIL' if pid in errors else 'OK  '} {pid}  {post.get('scheduled_for', '')}  {post.get('content_type', '')}")
        for line in errors.get(pid, []):
            print(f"       x {line}")
        for line in warnings.get(pid, []):
            print(f"       ! {line}")
    for line in general:
        print(f"! {line}")
    print(f"\n{len(data['posts'])} posts, {len(errors)} with errors.")
    return 1 if errors else 0


def payload_for(post: dict, data: dict) -> dict:
    body = {
        "type": "gbp_post", "id": post["id"], "business": data.get("business", ""),
        "scheduledFor": post["scheduled_for"], "timezone": post.get("timezone", ""),
        "languageCode": data.get("languageCode", "en"),
        "topicType": post["topicType"], "summary": post["summary"].strip(),
        "callToAction": post.get("callToAction") or None,
        "media": [m for m in post.get("media") or [] if m.get("sourceUrl")],
    }
    if post["topicType"] == "OFFER":
        body["offer"] = post.get("offer")
    return body


def send(args) -> int:
    load_env()
    data = load_posts(args.file)
    errors, _, _ = check(data["posts"])
    posts = [p for p in data["posts"] if not args.only or p.get("id") in args.only]
    blocked = [p["id"] for p in posts if p.get("id") in errors]
    if blocked:
        raise SystemExit(f"Not sending: {blocked} fail validation. Run `gbp_posts.py validate`.")
    posts = [p for p in posts if p.get("status") != "sent" or args.resend]
    url = os.environ.get("MAKE_GBP_POST_WEBHOOK_URL", "")
    if args.send and not url:
        raise SystemExit("MAKE_GBP_POST_WEBHOOK_URL is not set (environment or project .env).")

    if not args.send:
        print(f"DRY RUN - {len(posts)} posts would go to "
              f"{'the Make webhook' if url else 'the Make webhook (MAKE_GBP_POST_WEBHOOK_URL not set yet)'}.\n")
        for post in posts:
            print(json.dumps(payload_for(post, data), indent=2, ensure_ascii=False))
        print("\nNothing was sent. Add --send to dispatch.")
        return 0

    headers = {"x-make-apikey": os.environ["MAKE_WEBHOOK_API_KEY"]} if os.environ.get("MAKE_WEBHOOK_API_KEY") else {}
    failures = 0
    for post in posts:
        status, body = http_post_json(url, payload_for(post, data), headers=headers)
        ok = 200 <= status < 300
        failures += not ok
        post["status"] = "sent" if ok else "send_failed"
        print(f"{'sent  ' if ok else 'FAILED'} {post['id']}  HTTP {status}  {body[:120]}")
    write_json(Path(args.file), data)
    print(f"\n{len(posts) - failures} sent, {failures} failed. Statuses saved to {args.file}.")
    return 1 if failures else 0


def main(argv=None) -> int:
    utf8_stdout()
    parser = argparse.ArgumentParser(description="Plan, validate and dispatch a month of GBP posts.")
    parser.add_argument("--file", default=str(DEFAULT_FILE), help=f"Posts file (default {DEFAULT_FILE}).")
    parser.add_argument("--business", default=None)
    sub = parser.add_subparsers(dest="command", required=True)
    p_plan = sub.add_parser("plan")
    p_plan.add_argument("--start", help="First week, YYYY-MM-DD (default: next Monday).")
    p_plan.add_argument("--weeks", type=int, default=4)
    p_plan.add_argument("--per-week", type=int, default=3, choices=[2, 3])
    p_plan.add_argument("--time", default="10:00", help="Local publish time HH:MM (default 10:00).")
    p_plan.add_argument("--force", action="store_true")
    sub.add_parser("validate")
    p_send = sub.add_parser("send")
    p_send.add_argument("--send", action="store_true", help="Really dispatch. Without it this is a dry run.")
    p_send.add_argument("--only", nargs="*", help="Post ids to send.")
    p_send.add_argument("--resend", action="store_true", help="Include posts already marked sent.")
    args = parser.parse_args(argv)
    return {"plan": plan, "validate": validate, "send": send}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
