---
description: "Build Service x City landing pages with local proof, quote form and LocalBusiness/Service schema, gated against doorway pages"
argument-hint: "<service> in <city> | all"
---

Run the `/service-page` module of the **local-seo** skill.

1. Load the `local-seo` skill (`SKILL.md`) and follow its rules.
2. Read `local-seo/business.json` in this project. If it is missing, create it from the skill's `templates/business.example.json` and fill it in with the user before going further.
3. Read the skill's `references/service-page.md` and follow it. Scripts are in the skill's `scripts/` folder; run them from this project's root.

Write the page data file(s), collect real testimonials and projects from the user, and pass `doorway_check.py` before marking anything ready.

Arguments: $ARGUMENTS
