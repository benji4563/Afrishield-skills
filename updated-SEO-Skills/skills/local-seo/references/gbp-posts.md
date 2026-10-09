# /gbp-posts - a month of Google Business Profile posts

Eight to twelve posts, two or three a week, drafted in one sitting, validated,
then dispatched to a Make.com webhook that publishes them on schedule.

## 1. Plan the slots

```
python scripts/gbp_posts.py plan --start 2026-11-02 --per-week 3
```

Writes `local-seo/output/gbp-posts.json`: 12 slots (8 with `--per-week 2`) on
Mon/Wed/Fri at 10:00 local, rotating the mix below and cycling through the
services in `business.json`.

| `content_type` | What it is | `topicType` |
|---|---|---|
| `service_highlight` | One service, told through a local job | `STANDARD` |
| `offer` | Limited-time or seasonal offer | `OFFER` |
| `tip` | One useful thing the customer can do or check | `STANDARD` |
| `local_news` | Local business or community news with a real link to the business | `STANDARD` |

## 2. Write the drafts

Fill `summary` (and `target_keyword`, `media`, and `offer` where present) for
every slot.

- **The first 100 characters carry the post** - that is all that shows before
  "more". Lead with the place and the point.
- 80 to 300 words is plenty; the limit is 1,500 characters.
- Name a neighbourhood or landmark in every post. Use the slot's target keyword
  once, from `keyword-map.json`.
- **Service highlights use real jobs only.** Ask the user for recent jobs
  (area, problem, what was done, result). If none are available, write the post
  about the service and how it is done locally - do not invent a case study.
- **Offers are the client's to make.** Draft only offers the owner has
  confirmed, with real dates and terms. Never invent a discount.
- **Local news must be true and checkable.** Search for it; link the source.
- **No phone numbers in the text** - Google rejects those posts. Use the `CALL`
  button instead.
- Every post gets a photo URL (`media[0].sourceUrl`, public https, at least
  400x300; 1200x900 looks best). Real job photos beat stock.
- `callToAction.actionType` is one of `BOOK`, `ORDER`, `SHOP`, `LEARN_MORE`,
  `SIGN_UP`, `CALL`. Point `url` at the matching Service x City page.
- No two posts open with the same words.

## 3. Validate

```
python scripts/gbp_posts.py validate
```

Fix every `x` line. `!` lines are judgement calls. Then show the user all the
drafts and get approval of the month before anything is sent.

## 4. Dispatch

```
python scripts/gbp_posts.py send            # dry run - prints the payloads
python scripts/gbp_posts.py send --send     # after the user says yes
```

Needs `MAKE_GBP_POST_WEBHOOK_URL` in `.env`. Sent posts are marked
`"status": "sent"` in the file and skipped next time (`--resend` overrides;
`--only post-03` sends one).

Payload per post (mirrors the Business Profile `localPosts` resource):

```json
{
  "type": "gbp_post",
  "id": "post-01",
  "business": "Business Name",
  "scheduledFor": "2026-11-02T10:00:00",
  "timezone": "America/Toronto",
  "languageCode": "en",
  "topicType": "STANDARD",
  "summary": "...",
  "callToAction": { "actionType": "LEARN_MORE", "url": "https://example.com/services/drain-cleaning/etobicoke" },
  "media": [{ "mediaFormat": "PHOTO", "sourceUrl": "https://example.com/photos/job.webp" }],
  "offer": { "title": "...", "couponCode": "", "redeemOnlineUrl": "...", "termsConditions": "...", "startDate": "2026-11-06", "endDate": "2026-11-20" }
}
```

`offer` is present only on `OFFER` posts.

## Make.com scenario C - scheduled publishing

Two small scenarios, because a webhook run cannot wait days.

**C1 - intake**

| # | Module | Settings |
|---|---|---|
| 1 | **Webhooks > Custom webhook** | URL goes in `MAKE_GBP_POST_WEBHOOK_URL` |
| 2 | **Filter** | `type` equals `gbp_post` |
| 3 | **Data store > Add/replace a record** | Key = `id`; store every field plus `published = false` |

**C2 - publisher** (scheduled, every hour)

| # | Module | Settings |
|---|---|---|
| 1 | **Data store > Search records** | `published = false` and `scheduledFor <= now` |
| 2 | **Google Business Profile > Create a Post** | Map `topicType`, `summary`, `callToAction`, `media`, and the offer fields for `OFFER` posts |
| 3 | **Data store > Update a record** | `published = true` |
| 4 | *(optional)* **Slack > Create a message** | "Posted: {{summary}}" |

A Google Sheet works in place of the data store if the owner wants to see and
edit the queue.

## Next month

Run `plan` again with a new `--start` and `--file local-seo/output/gbp-posts-<month>.json`.
Rotate services so each gets a highlight every two months, and reuse nothing
word for word.
