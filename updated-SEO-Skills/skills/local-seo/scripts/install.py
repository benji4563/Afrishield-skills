#!/usr/bin/env python3
"""
install.py — install the local-seo skill and its slash commands into a project.

Copies
  skills/local-seo/        -> <target>/.claude/skills/local-seo/
  commands/*.md            -> <target>/.claude/commands/
  templates/business.example.json -> <target>/local-seo/business.json   (only if missing)

With --templates it also copies the Next.js Service x City and review-form
templates into the project (app/, components/, lib/, content/). Existing files
are never overwritten unless --force is given.

Usage
  python install.py --target "C:/path/to/client-site"
  python install.py --target "C:/path/to/client-site" --templates
  python install.py --target . --templates --force
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent           # skills/local-seo
PLUGIN_DIR = SKILL_DIR.parent.parent                          # plugin root
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", "node_modules", ".next")


def copy_tree(source: Path, destination: Path, force: bool) -> tuple[int, int]:
    copied = skipped = 0
    for path in source.rglob("*"):
        if path.is_dir() or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        target = destination / path.relative_to(source)
        if target.exists() and not force:
            skipped += 1
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        copied += 1
    return copied, skipped


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Install the local-seo skill into a project.")
    parser.add_argument("--target", required=True, help="Project folder (the client site or workspace).")
    parser.add_argument("--templates", action="store_true", help="Also copy the Next.js templates into the project.")
    parser.add_argument("--force", action="store_true", help="Overwrite files that already exist.")
    args = parser.parse_args(argv)

    target = Path(args.target).resolve()
    if not target.is_dir():
        raise SystemExit(f"Target folder does not exist: {target}")

    skill_target = target / ".claude" / "skills" / "local-seo"
    if skill_target.resolve() != SKILL_DIR:
        if skill_target.exists():
            shutil.rmtree(skill_target)  # the skill itself is always refreshed
        shutil.copytree(SKILL_DIR, skill_target, ignore=IGNORE)
        print(f"skill     -> {skill_target}")

    commands_source = PLUGIN_DIR / "commands"
    if commands_source.is_dir():
        commands_target = target / ".claude" / "commands"
        commands_target.mkdir(parents=True, exist_ok=True)
        names = []
        for command in sorted(commands_source.glob("*.md")):
            shutil.copy2(command, commands_target / command.name)
            names.append("/" + command.stem)
        print(f"commands  -> {commands_target}  ({' '.join(names)})")
    else:
        print("commands  -> not found next to the skill; slash commands were not installed")

    business = target / "local-seo" / "business.json"
    if business.exists():
        print(f"business  -> kept existing {business}")
    else:
        business.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SKILL_DIR / "templates" / "business.example.json", business)
        print(f"business  -> {business}  (fill this in first)")

    if args.templates:
        copied, skipped = copy_tree(SKILL_DIR / "templates" / "nextjs", target, args.force)
        print(f"templates -> {copied} files copied into {target}"
              + (f", {skipped} already existed and were kept (use --force to overwrite)" if skipped else ""))

    print("\nNext: fill in local-seo/business.json, restart Claude Code in the project, then run /gbp.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
