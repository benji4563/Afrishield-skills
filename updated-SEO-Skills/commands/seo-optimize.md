---
description: "Fix technical, on-page, schema and GEO issues until the audit is clean (Lighthouse 90+, verified FAQPage, citable definition blocks)"
argument-hint: "[URL or site root]"
---

Run the `/seo-optimize` module of the **local-seo** skill.

1. Load the `local-seo` skill (`SKILL.md`) and follow its rules.
2. Read `local-seo/business.json` in this project. If it is missing, create it from the skill's `templates/business.example.json` and fill it in with the user before going further.
3. Read the skill's `references/seo-geo-audit.md` and follow it. Scripts are in the skill's `scripts/` folder; run them from this project's root.

Run the audit, fix every FAIL in the code, and re-run until clean. Report what changed.

Arguments: $ARGUMENTS
