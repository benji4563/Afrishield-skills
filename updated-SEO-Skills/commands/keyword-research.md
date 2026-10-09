---
description: "Local keyword research: 4-step filter (volume, difficulty, intent, CPC) and clustering into Service x City pages and blog topics"
argument-hint: "[path to a Semrush/Ahrefs export, optional]"
---

Run the `/keyword-research` module of the **local-seo** skill.

1. Load the `local-seo` skill (`SKILL.md`) and follow its rules.
2. Read `local-seo/business.json` in this project. If it is missing, create it from the skill's `templates/business.example.json` and fill it in with the user before going further.
3. Read the skill's `references/keyword-research.md` and follow it. Scripts are in the skill's `scripts/` folder; run them from this project's root.

If an export path is given, use `filter --input`. Otherwise state the Apify cost and run. Report the page list for confirmation.

Arguments: $ARGUMENTS
