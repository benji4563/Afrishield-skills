---
description: "Draft, validate and dispatch a month of Google Business Profile posts (8-12, 2-3 a week)"
argument-hint: "[start date YYYY-MM-DD] [2|3 per week]"
---

Run the `/gbp-posts` module of the **local-seo** skill.

1. Load the `local-seo` skill (`SKILL.md`) and follow its rules.
2. Read `local-seo/business.json` in this project. If it is missing, create it from the skill's `templates/business.example.json` and fill it in with the user before going further.
3. Read the skill's `references/gbp-posts.md` and follow it. Scripts are in the skill's `scripts/` folder; run them from this project's root.

Plan the slots, write every draft, validate, and show the user the month. Dispatch only after they approve, dry run first.

Arguments: $ARGUMENTS
