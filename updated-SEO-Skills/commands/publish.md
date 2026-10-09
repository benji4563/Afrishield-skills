---
description: "Pre-flight checks, push to GitHub and deploy to Vercel with automatic SSL"
argument-hint: "[preview | prod]"
---

Run the `/publish` module of the **local-seo** skill.

1. Load the `local-seo` skill (`SKILL.md`) and follow its rules.
2. Read `local-seo/business.json` in this project. If it is missing, create it from the skill's `templates/business.example.json` and fill it in with the user before going further.
3. Read the skill's `references/publish-syndicate.md` and follow it. Scripts are in the skill's `scripts/` folder; run them from this project's root.

Follow the /publish section. Run the pre-flight, then confirm with the user before pushing and before a production deploy.

Arguments: $ARGUMENTS
