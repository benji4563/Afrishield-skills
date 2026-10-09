# /review-engine - review intake, Slack alerts and review replies

Three pieces: the intake form customers are sent to, a Make.com scenario that
puts private feedback in Slack, and a Make.com scenario that handles public
Google reviews.

## 1. The intake form

Two versions, same behaviour:

| Version | File | Use when |
|---|---|---|
| Next.js | `templates/nextjs/app/review/page.tsx`, `components/local-seo/ReviewGate.tsx`, `app/api/review-feedback/route.ts` | the site is Next.js; the webhook URL stays on the server |
| Standalone | `templates/review-form/review.html` | any other site; one file, no build. Edit `CONFIG` at the top. The webhook URL is visible in page source |

Behaviour:

- A 1-5 star rating.
- **4 or 5 stars:** a thank-you, then an automatic redirect to
  `gbp.review_link` (`https://g.page/r/<id>/review`) after 1.5 seconds, with a
  button as fallback.
- **1 to 3 stars:** a private feedback form. On submit the payload is POSTed to
  the Make.com webhook, which alerts the private Slack channel.
- The page is `noindex`. Link to it from review-request emails, texts and QR
  codes, with `?ref=<job or service>` to carry context into the alert.

Install with `python scripts/install.py --target <project> --templates`, set
`gbp.review_link` in `business.json` and `MAKE_REVIEW_WEBHOOK_URL` in `.env`.

### The Google link stays visible to everyone

Low raters see a small "Prefer to post publicly? Leave a Google review" link
under the feedback form (`publicLinkForAll`, on by default). Leave it on.

Google's review policy prohibits "selectively soliciting positive reviews" and
discouraging negative ones. A form that only shows the Google link to happy
customers is that practice ("review gating"), and the penalty is removal of
reviews or suspension of the profile - the asset this whole suite is building.
With the link visible to all, the form still does its job: happy customers are
carried straight to Google, unhappy ones are offered a faster route to a
manager, and nobody is blocked. If a client insists on turning it off, tell them
the risk plainly and let them decide; do not turn it off on your own.

### Webhook payload (1-3 stars)

```json
{
  "type": "review_feedback",
  "business": "Business Name",
  "rating": 2,
  "feedback": "Technician arrived two hours late.",
  "name": "Customer name",
  "contact": "phone or email",
  "context": "drain-cleaning-etobicoke",
  "page_url": "https://example.com/review?ref=drain-cleaning-etobicoke",
  "submitted_at": "2026-10-09T14:03:11.000Z"
}
```

## 2. Make.com scenario A - private feedback to Slack

| # | Module | Settings |
|---|---|---|
| 1 | **Webhooks > Custom webhook** | Create it, copy the URL into `MAKE_REVIEW_WEBHOOK_URL`. Send one test submission so Make learns the fields. Optional: enable API-key auth and set `MAKE_WEBHOOK_API_KEY` |
| 2 | **Filter** | `type` equals `review_feedback` and `rating` is less than 4 |
| 3 | **Slack > Create a message** | Private channel, e.g. `#reviews-private`. Text below |
| 4 | *(optional)* **Google Sheets > Add a row** | A log, so resolution can be tracked |

Slack message:

```
:warning: {{rating}}-star private feedback - {{business}}
> {{feedback}}
From: {{name}} ({{contact}})   Context: {{context}}
Submitted: {{submitted_at}}
Reply to the customer within one business day. React with a tick when resolved.
```

## 3. Make.com scenario B - public Google reviews

| # | Module | Settings |
|---|---|---|
| 1 | **Google Business Profile > Watch Reviews** | The client's location; run every 15 minutes |
| 2 | **Router** | Two routes on `starRating`. The API returns words, not numbers: `ONE` ... `FIVE` |
| 3a | Route **positive**: `starRating` is `FOUR` or `FIVE` | |
| 4a | **Anthropic Claude > Create a message** (or any LLM module) | Prompt below |
| 5a | **Google Business Profile > Reply to a Review** | Reply text = the model's output |
| 3b | Route **negative**: `starRating` is `ONE`, `TWO` or `THREE` | |
| 4b | **Slack > Create a message** | Private channel: reviewer, rating, full comment, link to the review. **No auto-reply** |

Prompt for 4a - fill the bracketed parts from `business.json` and the keyword map:

```
Write a reply to this Google review for [business name], a [category] serving
[primary metro and 3-4 service areas].

Review by {{reviewer.displayName}}, {{starRating}} stars:
"{{comment}}"

Rules:
- 2 to 3 sentences, under 60 words. Warm, specific, written by a person.
- Thank them by first name and refer to something they actually said.
- If they named a service or a place, repeat it naturally. If they did not,
  mention at most one of these where it fits: [3-5 service + area phrases].
  Never more than one, never forced, never a list.
- If the review has no text, thank them briefly and stop.
- No offers, no links, no phone numbers, no emoji, no "we strive".
- Do not confirm they are a customer beyond what they said; add no private details.
Return only the reply text.
```

Why negative reviews are never auto-answered: a 1-3 star reply is read by every
future customer, and a wrong or defensive one does more damage than the review.
The Slack alert asks a person to reply within 24 hours. When asked to draft one,
write it for the owner to post: acknowledge the specific problem, no excuses and
no arguing the facts, say what has been or will be done, and move the detail
offline with a named person and a direct contact.

Before the positive route goes live, run it with step 5a disabled for a week so
the owner can read what it would have posted.

## 4. Review requests

The form does nothing until customers are sent to it. Draft, for the owner's
approval, one short SMS and one email sent within 24 hours of a finished job,
each linking to `/review?ref=<service>`. Ask every customer, not a selected
few - same policy, same reason. Offering a reward for a review is prohibited.

## Checks before handing over

- Submit a 2-star test: Slack message arrives with every field.
- Click 5 stars: lands on the Google review form for the right business.
- `curl -s <site>/review | grep -i noindex` finds the tag.
