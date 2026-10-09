#!/usr/bin/env python3
"""
syndicate.py — turn a published local post into LinkedIn, X and Facebook posts.

The agent writes the platform copy into local-seo/social/<slug>.json; this
script checks it against each platform's limits and dispatches it.

  {
    "source_url": "https://example.com/blog/spring-drain-checklist-etobicoke",
    "title": "Spring drain checklist for Etobicoke homes",
    "image_url": "https://example.com/blog/spring-drain-checklist/hero.webp",
    "posts": {
      "linkedin": {"text": "..."},
      "x":        {"text": "...", "thread": ["...", "..."]},
      "facebook": {"text": "..."}
    }
  }

Subcommands
  validate  Check lengths, link, image and that the three posts are not copies.
  accounts  List connected Blotato accounts and pages (to fill in the env ids).
  send      Dispatch. Dry run unless --send is given.

Dispatch routes (--via)
  blotato   Blotato REST API. Needs BLOTATO_API_KEY plus the account ids:
            BLOTATO_LINKEDIN_ACCOUNT_ID [BLOTATO_LINKEDIN_PAGE_ID]
            BLOTATO_TWITTER_ACCOUNT_ID
            BLOTATO_FACEBOOK_ACCOUNT_ID  BLOTATO_FACEBOOK_PAGE_ID
  webhook   One JSON POST per platform to SOCIAL_WEBHOOK_URL (Make.com, n8n,
            Zapier, or any scheduler with an inbound webhook).

Usage
  python syndicate.py validate local-seo/social/spring-drain-checklist-etobicoke.json
  python syndicate.py accounts
  python syndicate.py send local-seo/social/<slug>.json                       # dry run
  python syndicate.py send local-seo/social/<slug>.json --send --via blotato
  python syndicate.py send local-seo/social/<slug>.json --send --schedule 2026-11-03T14:00:00Z
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

from _common import http_get, http_post_json, load_env, utf8_stdout

BLOTATO = "https://backend.blotato.com/v2"
LIMITS = {"linkedin": 3000, "x": 280, "facebook": 63206}
RECOMMENDED = {"linkedin": 1300, "facebook": 500}
BLOTATO_PLATFORM = {"linkedin": "linkedin", "x": "twitter", "facebook": "facebook"}
URL = re.compile(r"https?://\S+")


def x_length(text: str) -> int:
    """X counts every link as 23 characters."""
    return len(URL.sub("x" * 23, text))


def check(data: dict) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    source = data.get("source_url", "")
    if not source.startswith("https://"):
        errors.append("source_url must be the live https:// URL of the published post")
    image = data.get("image_url", "")
    if not image:
        warnings.append("no image_url - posts with an image travel further")
    elif not image.startswith("https://"):
        errors.append("image_url must be a public https:// URL")
    posts = data.get("posts") or {}
    for platform in ("linkedin", "x", "facebook"):
        post = posts.get(platform)
        if not post or not (post.get("text") or "").strip():
            errors.append(f"{platform}: no text")
            continue
        text = post["text"]
        length = x_length(text) if platform == "x" else len(text)
        if length > LIMITS[platform]:
            errors.append(f"{platform}: {length} chars (limit {LIMITS[platform]})")
        elif platform in RECOMMENDED and length > RECOMMENDED[platform]:
            warnings.append(f"{platform}: {length} chars (reads best under {RECOMMENDED[platform]})")
        if re.search(r"\{\{|\bTODO\b", text):
            errors.append(f"{platform}: placeholder text")
        thread = post.get("thread") or []
        for number, part in enumerate(thread, start=2):
            if x_length(part) > LIMITS["x"]:
                errors.append(f"x: thread post {number} is {x_length(part)} chars (limit 280)")
        if source and source not in " ".join([text, *thread]):
            warnings.append(f"{platform}: does not link back to the post")
    texts = [posts[p]["text"].strip() for p in ("linkedin", "x", "facebook") if posts.get(p, {}).get("text")]
    if len(texts) > 1 and len(set(texts)) < len(texts):
        errors.append("two platforms carry identical copy - write each for its platform")
    return errors, warnings


def blotato_body(platform: str, post: dict, data: dict, schedule: str | None) -> dict:
    name = BLOTATO_PLATFORM[platform]
    account = os.environ.get(f"BLOTATO_{name.upper()}_ACCOUNT_ID", "")
    if not account:
        raise SystemExit(f"BLOTATO_{name.upper()}_ACCOUNT_ID is not set. Run `syndicate.py accounts`.")
    target = {"targetType": name}
    page = os.environ.get(f"BLOTATO_{name.upper()}_PAGE_ID", "")
    if name == "facebook":
        if not page:
            raise SystemExit("BLOTATO_FACEBOOK_PAGE_ID is not set (Facebook needs a page). Run `syndicate.py accounts`.")
        target["pageId"] = page
    elif name == "linkedin" and page:
        target["pageId"] = page
    media = [data["image_url"]] if data.get("image_url") else []
    content = {"text": post["text"], "mediaUrls": media, "platform": name}
    if name == "twitter" and post.get("thread"):
        content["additionalPosts"] = [{"text": part, "mediaUrls": []} for part in post["thread"]]
    body = {"post": {"accountId": account, "content": content, "target": target}}
    if schedule:
        body["scheduledTime"] = schedule
    return body


def webhook_body(platform: str, post: dict, data: dict, schedule: str | None) -> dict:
    return {"type": "social_post", "platform": platform, "text": post["text"], "thread": post.get("thread") or [],
            "image_url": data.get("image_url", ""), "source_url": data.get("source_url", ""),
            "title": data.get("title", ""), "scheduled_time": schedule}


def accounts() -> int:
    load_env()
    key = os.environ.get("BLOTATO_API_KEY")
    if not key:
        raise SystemExit("BLOTATO_API_KEY is not set (environment or project .env).")
    headers = {"blotato-api-key": key}
    status, body = http_get(f"{BLOTATO}/users/me/accounts", headers=headers)
    if status != 200:
        raise SystemExit(f"Blotato returned HTTP {status}: {body[:200]}")
    for account in json.loads(body).get("items", []):
        print(f"{account.get('platform', ''):10} accountId {account.get('id')}  {account.get('username') or account.get('fullname') or ''}")
        if account.get("platform") in ("facebook", "linkedin"):
            sub_status, sub_body = http_get(f"{BLOTATO}/users/me/accounts/{account['id']}/subaccounts", headers=headers)
            if sub_status == 200:
                for page in json.loads(sub_body).get("items", []):
                    print(f"{'':10}   pageId {page.get('id')}  {page.get('name', '')}")
    return 0


def main(argv=None) -> int:
    utf8_stdout()
    parser = argparse.ArgumentParser(description="Validate and dispatch social posts for a published article.")
    sub = parser.add_subparsers(dest="command", required=True)
    p_validate = sub.add_parser("validate")
    p_validate.add_argument("file")
    sub.add_parser("accounts")
    p_send = sub.add_parser("send")
    p_send.add_argument("file")
    p_send.add_argument("--via", choices=["blotato", "webhook"], default="blotato")
    p_send.add_argument("--platforms", nargs="*", default=["linkedin", "x", "facebook"], choices=["linkedin", "x", "facebook"])
    p_send.add_argument("--schedule", help="ISO 8601 UTC time, e.g. 2026-11-03T14:00:00Z (default: post now).")
    p_send.add_argument("--send", action="store_true", help="Really dispatch. Without it this is a dry run.")
    args = parser.parse_args(argv)

    if args.command == "accounts":
        return accounts()

    path = Path(args.file)
    data = json.loads(path.read_text(encoding="utf-8"))
    errors, warnings = check(data)
    for line in errors:
        print(f"x {line}")
    for line in warnings:
        print(f"! {line}")
    if args.command == "validate":
        posts = data.get("posts") or {}
        for platform in ("linkedin", "x", "facebook"):
            text = (posts.get(platform) or {}).get("text", "")
            print(f"{platform:9} {x_length(text) if platform == 'x' else len(text):5} / {LIMITS[platform]} chars")
        print("FAIL" if errors else "OK")
        return 1 if errors else 0
    if errors:
        raise SystemExit("Not sending: fix the errors above.")

    load_env()
    build = blotato_body if args.via == "blotato" else webhook_body
    if not args.send:
        print(f"DRY RUN via {args.via} - nothing will be posted.\n")
        if args.via == "webhook":
            for platform in args.platforms:
                print(json.dumps(build(platform, data["posts"][platform], data, args.schedule), indent=2, ensure_ascii=False))
        else:
            for platform in args.platforms:
                post = data["posts"][platform]
                print(f"[{platform}] {x_length(post['text']) if platform == 'x' else len(post['text'])} chars"
                      f"{', thread of ' + str(len(post['thread']) + 1) if post.get('thread') else ''}\n{post['text']}\n")
        print("Add --send to dispatch.")
        return 0

    if args.via == "blotato":
        key = os.environ.get("BLOTATO_API_KEY")
        if not key:
            raise SystemExit("BLOTATO_API_KEY is not set (environment or project .env).")
        url, headers = f"{BLOTATO}/posts", {"blotato-api-key": key}
    else:
        url, headers = os.environ.get("SOCIAL_WEBHOOK_URL", ""), {}
        if not url:
            raise SystemExit("SOCIAL_WEBHOOK_URL is not set (environment or project .env).")

    failures = 0
    for platform in args.platforms:
        status, body = http_post_json(url, build(platform, data["posts"][platform], data, args.schedule), headers=headers)
        ok = 200 <= status < 300
        failures += not ok
        print(f"{'sent  ' if ok else 'FAILED'} {platform}  HTTP {status}  {body[:160]}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
