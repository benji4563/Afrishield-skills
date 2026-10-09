---
description: "Turn a published post into LinkedIn, X and Facebook posts with an image and dispatch them via Blotato or a webhook"
argument-hint: "<published post URL>"
---

Run the `/syndicate` module of the **local-seo** skill.

1. Load the `local-seo` skill (`SKILL.md`) and follow its rules.
2. Read `local-seo/business.json` in this project. If it is missing, create it from the skill's `templates/business.example.json` and fill it in with the user before going further.
3. Read the skill's `references/publish-syndicate.md` and follow it. Scripts are in the skill's `scripts/` folder; run them from this project's root.

Follow the /syndicate section. Write the three posts, validate, show the dry run, and send only after the user approves.

Arguments: $ARGUMENTS
