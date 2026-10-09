# /blog-post - local topical authority and dwell time

Informational posts for people in the service area who are not buying yet:
seasonal preparation, permit and bylaw explainers, neighbourhood and event
guides, "what to do when" checklists. Their jobs are to reach local readers
early, keep them reading, and pass link equity to the Service x City pages.

The base site's blog pipeline (routes, components, image generation, commit
conventions) is in the `ai-seo-website-builder` skill, Phase 6. This file covers
what makes a post *local* and how it is linked.

## 1. Pick the topic

From `blog_topics` in `keyword-map.json`. Each has a primary keyword,
secondaries and `link_to` (the money pages it supports). Prefer topics that:

- have a `link_to` target that is already live;
- are specific to the place ("when does Etobicoke flush hydrants", not "what is
  a hydrant");
- are seasonal and due in the next four to six weeks.

Topic types that work locally: seasonal preparation for this climate; permit,
bylaw and rebate rules for this municipality; cost guides with local numbers;
event and neighbourhood guides where the business has a real connection;
"who is responsible" questions (city vs homeowner). Skip a topic the business
has no standing to write about.

Check the client's used-keywords log first; never reuse a primary.

## 2. Research

- Search the primary keyword; read the top three results for structure only
  (format, headings, what they miss). Never reuse their sentences.
- Verify every local fact at the source: the municipality, the utility, the
  event's own page. Link those sources in the post. Date anything that changes.
- Ask the client for one real story or observation on the topic. One true local
  detail is worth more than three paragraphs of general advice.

## 3. Write

- **1,200 to 2,000 words**, in the business's voice. Load the
  `seo-blog-humor-style` skill for tone: relatable framing and light humour
  where the subject allows it, never on safety, money loss or legal topics.
- **Open with a direct answer block** of 40 to 70 words: the question answered
  plainly. That is what Google's AI Overviews and assistants quote. The story
  comes after.
- **Every H2 section starts with its answer** in a sentence or two, then the
  detail.
- Use at least one comparison table or step list, and name real streets,
  neighbourhoods, seasons and local institutions throughout.
- Write for the reader who stays: short paragraphs, a concrete example early, a
  checklist they can act on, the surprising fact before the obvious one. Dwell
  time comes from being useful and readable, not from padding.
- **FAQ:** 4 to 6 questions from People Also Ask, with `FAQPage` JSON-LD built
  from the same items that are visible.
- JSON-LD: `BlogPosting` + `FAQPage` + `BreadcrumbList`.
- No invented statistics, quotes, customers or prices.

## 4. Internal links - the point of the post

| Link | Rule |
|---|---|
| To the money page | At least one contextual link to each `link_to` Service x City page, in the body, within the first half of the post |
| Anchor text | Describes the destination and varies between posts: "drain cleaning in Etobicoke", "our Etobicoke drain crew" - never "click here", never the same exact-match anchor every time |
| Placement | Where the reader's problem becomes one the service solves. One link per target per post, two at most |
| Sideways | One or two links to related posts that exist |
| Back | Add a link from the Service x City page (or the service hub) to the new post, so equity and readers flow both ways |

A post with no link to a money page fails the audit below.

## 5. Verify

```
python scripts/geo_audit.py --url http://localhost:3000/blog/<slug>
```

Must pass, including `blog links to a service page`, `definition block` and
`FAQPage verified`. Then add the post to the sitemap, log the primary keyword
as used, and hand the URL to `/syndicate` once it is live.
