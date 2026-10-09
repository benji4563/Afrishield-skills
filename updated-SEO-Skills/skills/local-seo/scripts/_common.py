"""Shared helpers for the local-seo scripts. Standard library only."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

USER_AGENT = "AfriShield-LocalSEO/1.0 (+https://afrishieldai.com)"
BROWSER_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
KEYWORD_FINDER = Path("00 Knowledge") / "Keyword Finder"
DEFAULT_BUSINESS = Path("local-seo") / "business.json"
DEFAULT_OUT = Path("local-seo") / "output"


def utf8_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except AttributeError:
            pass


def afrishield_root() -> Path | None:
    """Folder that holds '00 Knowledge/Keyword Finder' (AFRISHIELD_ROOT overrides)."""
    override = os.environ.get("AFRISHIELD_ROOT")
    starts = [Path(override)] if override else []
    starts += [Path.cwd(), Path(__file__).resolve().parent]
    for start in starts:
        for folder in (start, *start.parents):
            if (folder / KEYWORD_FINDER / "keyword_orchestrator.py").is_file():
                return folder
    return None


def keyword_finder_dir() -> Path | None:
    root = afrishield_root()
    return root / KEYWORD_FINDER if root else None


def load_dotenv(*paths: Path) -> None:
    """Read KEY=VALUE lines into os.environ without overriding what is already set."""
    for path in paths:
        if not path or not Path(path).is_file():
            continue
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def load_env() -> None:
    """Project .env files first, then the shared Keyword Finder .env (APIFY_TOKEN)."""
    finder = keyword_finder_dir()
    load_dotenv(Path.cwd() / ".env.local", Path.cwd() / ".env",
                finder / ".env" if finder else None)


def load_business(path: str | os.PathLike | None = None) -> dict:
    target = Path(path) if path else DEFAULT_BUSINESS
    if not target.is_file():
        raise SystemExit(
            f"Business config not found: {target}\n"
            "Create it from templates/business.example.json (install.py does this), "
            "or pass --business <file>.")
    return json.loads(target.read_text(encoding="utf-8"))


def out_dir(path: str | os.PathLike | None = None) -> Path:
    target = Path(path) if path else DEFAULT_OUT
    target.mkdir(parents=True, exist_ok=True)
    return target


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def city_name(area: str) -> str:
    """'Etobicoke, ON' -> 'Etobicoke'."""
    return area.split(",")[0].strip()


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def http_get(url: str, headers: dict | None = None, timeout: int = 20) -> tuple[int, str]:
    """GET returning (status, body). Status 0 means the request never completed."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.status, response.read().decode(charset, errors="replace")
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return 0, str(error)


def http_post_json(url: str, payload, headers: dict | None = None, timeout: int = 30) -> tuple[int, str]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT, **(headers or {})})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return 0, str(error)
