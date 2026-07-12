---
name: follow-up-tracker
description: Scan HubSpot for follow-up candidates, prioritize by urgency score, and draft personalized follow-up emails via Gmail with talking points from deal history.
---

# Follow-Up Tracker

Scan the CRM for deals and contacts that need follow-up. Score each by urgency, generate personalized email drafts with talking points pulled from deal history, and present a prioritized action list.

## Trigger

User asks for follow-ups, asks what needs attention today, requests a follow-up list, or asks to draft outreach for stale deals.

## Execution

### Step 1: Identify follow-up candidates

Pull open deals sorted by last activity (oldest first):

```sql
SELECT hs_object_id, dealname, dealstage, amount, deal_currency_code,
       hubspot_owner_id, closedate, createdate,
       hs_lastmodifieddate, notes_last_updated,
       num_associated_contacts
FROM DEAL
WHERE dealstage NOT IN ('closedwon', 'closedlost')
ORDER BY hs_lastmodifieddate ASC
```

Set `chatInsights`:
```json
{
  "userIntent": "identify deals needing follow-up and draft outreach emails",
  "satisfaction": "NEUTRAL"
}
```

Additionally, find deals with close dates approaching (within 14 days):

```sql
SELECT hs_object_id, dealname, dealstage, amount, deal_currency_code,
       hubspot_owner_id, closedate, hs_lastmodifieddate
FROM DEAL
WHERE dealstage NOT IN ('closedwon', 'closedlost')
  AND closedate BETWEEN '{today}' AND '{14_days_from_now}'
ORDER BY closedate ASC
```

### Step 2: Pull contact details for each candidate deal

For each follow-up candidate, retrieve the associated contacts:

```json
{
  "objectType": "CONTACT",
  "properties": ["hs_object_id", "firstname", "lastname", "email", "jobtitle", "company", "hs_lead_status", "lastmodifieddate", "notes_last_updated"],
  "filterGroups": [{
    "associatedWith": [{
      "objectType": "deals",
      "operator": "IN",
      "objectIdValues": [DEAL_ID_1, DEAL_ID_2, DEAL_ID_3]
    }]
  }],
  "limit": 200,
  "chatInsights": {
    "userIntent": "identify deals needing follow-up and draft outreach emails",
    "satisfaction": "NEUTRAL"
  }
}
```

Batch deal IDs (up to 100 per association filter) to minimize API calls.

### Step 3: Check recent email history

For each primary contact (first contact associated with the deal, or the one with the most senior title), check Gmail for recent correspondence:

```json
{
  "query": "to:{contact_email} OR from:{contact_email} newer_than:30d",
  "pageSize": 5,
  "view": "THREAD_VIEW_MINIMAL"
}
```

If threads are found, retrieve the most recent one for context:

```json
{
  "threadId": "{most_recent_thread_id}",
  "messageFormat": "FULL_CONTENT"
}
```

Extract from the last email exchange:
- What was discussed (subject + key points from body)
- Who sent the last message (us or them)
- Date of last message
- Any open questions or commitments made

### Step 4: Calculate urgency score

Score each follow-up candidate on a 0-100 scale:

| Factor | Weight | Scoring |
|---|---|---|
| **Days since last contact** | 30% | 0 days = 0pts, 3 days = 30pts, 7 days = 60pts, 14+ days = 100pts |
| **Deal value** | 25% | Bottom quartile = 25pts, Mid = 50pts, Top quartile = 75pts, Top 10% = 100pts |
| **Stage advancement pressure** | 20% | Lead = 20pts, Qualified = 40pts, Proposal = 70pts, Negotiation = 100pts |
| **Close date proximity** | 15% | 30+ days = 10pts, 14-30 days = 40pts, 7-14 days = 70pts, <7 days = 100pts, Overdue = 100pts |
| **Activity gap** | 10% | notes_last_updated older than hs_lastmodifieddate by 7+ days = 80pts (suggests system updates only, no human touch) |

**Urgency score** = weighted sum, capped at 100.

Urgency tiers:
- **80-100: URGENT** -- follow up today
- **60-79: HIGH** -- follow up within 48 hours
- **40-59: MEDIUM** -- follow up this week
- **0-39: LOW** -- monitor, no immediate action

### Step 5: Generate talking points

For each follow-up, compile talking points from available data:

1. **Last interaction summary:** What was discussed, any commitments made, open questions
2. **Deal context:** Current stage, value, how long in pipeline, close date
3. **Trigger event:** Why following up now (days since contact, approaching close date, stage milestone)
4. **Value proposition hook:** Based on deal stage:
   - Lead/Qualified: Share a relevant case study or industry insight for African markets
   - Proposal: Reference specific proposal elements, ask about decision timeline
   - Negotiation: Address potential objections, offer to connect with technical team or reference customer
5. **Ask:** One clear call-to-action (schedule a call, confirm next steps, introduce to DM)

### Step 6: Draft follow-up emails

For each URGENT and HIGH priority follow-up, draft a personalized email using Gmail's `create_draft`:

**Email structure:**

```
Subject: {contextual subject line -- not generic}

Hi {FirstName},

{Opening line referencing last interaction or relevant trigger}

{1-2 sentences of value -- insight, update, or resource relevant to their situation}

{Clear ask with specific next step}

Best regards,
{owner_name}
AfriShield
```

**Draft creation call:**

```json
{
  "to": ["{contact_email}"],
  "subject": "{contextual_subject}",
  "body": "{personalized_email_body}",
  "replyToMessageId": "{last_thread_message_id_if_replying}"
}
```

Important rules for email drafts:
- If there is an existing email thread, use `replyToMessageId` to continue the thread rather than starting a new one
- Subject lines must reference something specific (deal name, last topic, shared context) -- never use generic subjects like "Following up" or "Checking in"
- Keep emails under 150 words
- Include exactly one call-to-action
- Match the tone of previous correspondence (formal if they are formal, direct if they are direct)
- Do NOT send the emails -- only create drafts for the user to review

### Step 7: Output the follow-up list

Present the prioritized list:

```
AFRISHIELD FOLLOW-UP TRACKER
Generated: {today}
Total candidates: {count}
Drafts created: {draft_count}

--- URGENT (follow up today) ---

1. {Deal Name} | {Stage} | ${Amount} | Score: {score}/100
   Contact: {FirstName LastName}, {Title} at {Company}
   Email: {email}
   Last contact: {date} ({days} days ago) -- {summary}
   Trigger: {why this needs attention now}
   Talking points:
     - {point 1}
     - {point 2}
     - {point 3}
   Draft: Created -- Subject: "{subject}" [Draft ID: {id}]
   Action: {specific next step}

--- HIGH (within 48 hours) ---

2. {Deal Name} | {Stage} | ${Amount} | Score: {score}/100
   ...

--- MEDIUM (this week) ---

3. {Deal Name} | {Stage} | ${Amount} | Score: {score}/100
   Contact: {FirstName LastName}, {Title} at {Company}
   Last contact: {date} ({days} days ago)
   Talking points:
     - {point 1}
     - {point 2}
   Action: {specific next step}
   (No draft created -- review before drafting)

--- SUMMARY ---
URGENT: {count} deals (${value})
HIGH: {count} deals (${value})
MEDIUM: {count} deals (${value})
LOW: {count} deals (${value}) -- not shown, monitoring only

Total pipeline at risk of going cold: ${urgent + high value}
Drafts ready to review in Gmail: {draft_count}
```

## Notes

- **Draft safety:** This skill creates Gmail drafts only -- it never sends emails. The user must review and send each draft manually. Always confirm with the user before creating drafts.
- **Reply threading:** When a prior email thread exists with the contact, always use `replyToMessageId` to continue the thread. Starting a new thread when one exists looks unprofessional.
- **Owner filtering:** If the user says "my follow-ups," resolve their HubSpot owner ID via `search_owners` and filter deals by `hubspot_owner_id`. Only draft emails from their account.
- **Contact selection:** When a deal has multiple contacts, draft the follow-up to the most senior contact (by title) unless the last interaction was with a different contact -- in that case, continue with the existing thread contact.
- **Rate limiting:** Batch contact lookups and limit Gmail thread searches to avoid rate limits. Process up to 20 follow-up candidates per run. If more exist, note the overflow and offer to process the next batch.
- **Currency:** Always include `deal_currency_code` when displaying deal amounts. African deals may use USD, ZAR, NGN, KES, GHS, or other currencies.
- **Timezone awareness:** When suggesting follow-up timing, consider African business hours (WAT, CAT, EAT, SAST). Avoid scheduling follow-ups for weekends or public holidays in the prospect's country.
