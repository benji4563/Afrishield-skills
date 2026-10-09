---
description: "Write a local informational blog post that opens with a citable answer and links to its Service x City money page"
argument-hint: "[topic or primary keyword]"
---

Run the `/blog-post` module of the **local-seo** skill.

1. Load the `local-seo` skill (`SKILL.md`) and follow its rules.
2. Read `local-seo/business.json` in this project. If it is missing, create it from the skill's `templates/business.example.json` and fill it in with the user before going further.
3. Read the skill's `references/blog-post.md` and follow it. Scripts are in the skill's `scripts/` folder; run them from this project's root.

With no argument, pick the best unused topic from `keyword-map.json` and confirm it with the user first.

Arguments: $ARGUMENTS
