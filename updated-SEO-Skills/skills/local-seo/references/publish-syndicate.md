# /publish and /syndicate - deployment and distribution

## /publish - GitHub to Vercel

Pushing and deploying are outward-facing. Show the user what will go out and
get a yes before `git push` and before any production deploy.

### Pre-flight (all must pass)

```
python scripts/doorway_check.py
npm run build
npm run start
python scripts/geo_audit.py --url http://localhost:3000/ http://localhost:3000/services/<service>/<city>
git status
```

Check `git status` for secrets: `.env`, `.env.local` and
`local-seo/output/*_raw.json` must be ignored. `local-seo/business.json` is
committed - the build reads it.

### First deploy

1. **Repository.** The user creates an empty GitHub repo (no README), or with
   the GitHub CLI installed and signed in: `gh repo create <name> --private --source=. --remote=origin`.
2. **Push.**
   ```
   git add -A
   git commit -m "Add local SEO pages and review form"
   git remote add origin https://github.com/<user>/<repo>.git
   git push -u origin main
   ```
3. **Vercel.** Either import the repo at vercel.com/new (the user, signed in
   with GitHub - every later push then deploys itself), or from the terminal:
   ```
   vercel link
   vercel            # preview deployment
   vercel --prod     # production, after the preview checks out
   ```
4. **Environment variables** (Vercel > Project > Settings > Environment
   Variables, or `vercel env add <NAME> production`): `NEXT_PUBLIC_SITE_URL`,
   `MAKE_REVIEW_WEBHOOK_URL`, `QUOTE_WEBHOOK_URL`, optional
   `MAKE_WEBHOOK_API_KEY`, `GOOGLE_SITE_VERIFICATION`. The user enters secret
   values themselves. Redeploy after changing them.
5. **Domain and SSL.** Add the domain under Project > Settings > Domains. Point
   it by nameservers (`ns1.vercel-dns.com`, `ns2.vercel-dns.com`) or the A/CNAME
   records Vercel shows. The certificate is issued automatically, usually within
   a minute of DNS resolving. Make the apex the canonical host and `www` a
   redirect to it.

### After every deploy

```
python scripts/geo_audit.py --site https://<domain> --psi
```

Then submit a 2-star test through `/review` and confirm the Slack alert, send
one quote-form test, and in Search Console submit `sitemap.xml` and inspect one
new URL. Report the production URL and the audit totals.

## /syndicate - one post, three platforms

Turns a **published** post into LinkedIn, X and Facebook posts with an image,
and dispatches them through Blotato or any webhook-driven scheduler.

### 1. Write the copy

Create `local-seo/social/<slug>.json`:

```json
{
  "source_url": "https://example.com/blog/<slug>",
  "title": "Post title",
  "image_url": "https://example.com/blog/<slug>/hero.webp",
  "posts": {
    "linkedin": { "text": "..." },
    "x": { "text": "...", "thread": ["...", "..."] },
    "facebook": { "text": "..." }
  }
}
```

`source_url` must be live (check it returns 200). `image_url` is the post's
hero image at a public https URL.

| Platform | Limit | Write it as |
|---|---|---|
| LinkedIn | 3,000 (best under 1,300) | The owner speaking as a local tradesperson or professional: one observation from the job, what it means for local owners, then the link. Line breaks, no hashtag wall (3 at most) |
| X | 280, links count as 23 | The single most surprising fact, then the link. Optional `thread` of 2-4 follow-ups, each under 280 |
| Facebook | best under 500 | Neighbour to neighbour: name the area, the season, the practical tip, the link. This is where local community groups share from |

Three different posts, not one post three times - the validator rejects
identical copy. Carry over nothing the article does not say.

### 2. Validate and preview

```
python scripts/syndicate.py validate local-seo/social/<slug>.json
python scripts/syndicate.py send local-seo/social/<slug>.json            # dry run
```

Show the user the three posts. Send only after a yes.

### 3. Dispatch

**Blotato** (`--via blotato`, the default). In `.env`: `BLOTATO_API_KEY`, then
the ids, which `accounts` lists:

```
python scripts/syndicate.py accounts
```

```
BLOTATO_LINKEDIN_ACCOUNT_ID=    BLOTATO_LINKEDIN_PAGE_ID=      # page id optional: omit to post to the personal profile
BLOTATO_TWITTER_ACCOUNT_ID=
BLOTATO_FACEBOOK_ACCOUNT_ID=    BLOTATO_FACEBOOK_PAGE_ID=      # Facebook requires a page
```

```
python scripts/syndicate.py send local-seo/social/<slug>.json --send
python scripts/syndicate.py send local-seo/social/<slug>.json --send --schedule 2026-11-03T14:00:00Z
python scripts/syndicate.py send local-seo/social/<slug>.json --send --platforms linkedin facebook
```

It calls `POST https://backend.blotato.com/v2/posts` with the
`blotato-api-key` header, one request per platform; the image goes in
`mediaUrls` and an X thread in `additionalPosts`.

**Any other scheduler** (`--via webhook`): one JSON POST per platform to
`SOCIAL_WEBHOOK_URL` - a Make.com, n8n or Zapier webhook feeding Buffer,
Metricool, Postiz or the platforms' own modules:

```json
{ "type": "social_post", "platform": "linkedin", "text": "...", "thread": [],
  "image_url": "...", "source_url": "...", "title": "...", "scheduled_time": null }
```

Space the three platforms over a day or two rather than firing all at once, and
report what was posted or scheduled, where, and when.
