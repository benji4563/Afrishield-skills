---
description: "Set up the star-rating review form, the Slack alert for private feedback, and Make.com review replies"
argument-hint: "[next | html]"
---

Run the `/review-engine` module of the **local-seo** skill.

1. Load the `local-seo` skill (`SKILL.md`) and follow its rules.
2. Read `local-seo/business.json` in this project. If it is missing, create it from the skill's `templates/business.example.json` and fill it in with the user before going further.
3. Read the skill's `references/review-engine.md` and follow it. Scripts are in the skill's `scripts/` folder; run them from this project's root.

Install the form (Next.js by default, `html` for the standalone page), then walk the user through the Make.com scenarios and run the handover checks.

Arguments: $ARGUMENTS
