---
description: "Audit a page or site for technical SEO, on-page, schema, sitemap, AI-crawler access and GEO readiness - report only, no changes"
argument-hint: "<URL or site root>"
---

Run the `/audit` module of the **local-seo** skill.

1. Load the `local-seo` skill (`SKILL.md`) and follow its rules.
2. Read `local-seo/business.json` in this project. If it is missing, create it from the skill's `templates/business.example.json` and fill it in with the user before going further.
3. Read the skill's `references/seo-geo-audit.md` and follow it. Scripts are in the skill's `scripts/` folder; run them from this project's root.

Report only: run `geo_audit.py` (add `--psi` for a public site) and present the findings. Change nothing.

Arguments: $ARGUMENTS
