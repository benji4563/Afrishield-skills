---
name: deal-stage-analysis
description: Diagnose stuck deals in HubSpot -- categorize as Ghost, Single-threaded, No DM, or Email Dark -- with severity ratings and prescribed next actions.
---

# Deal Stage Analysis

Diagnose deals that are stuck or at risk of stalling. Categorize each issue, assign severity, and prescribe concrete next actions. Cross-references HubSpot deal activity with email engagement data.

## Trigger

User asks to analyze stuck deals, diagnose pipeline blockers, find deals at risk, or review deal health.

## Diagnosis Categories

| Category | Definition | Detection Logic |
|---|---|---|
| **Ghost** | Contact has gone silent -- no response to outreach in 7+ days | No inbound email activity and no notes/calls logged in last 7 days |
| **Single-threaded** | Only 1 contact associated with the deal -- no multi-threading | `num_associated_contacts` = 1 |
| **No DM** | No decision maker identified or tagged on the deal | No contact with role/title containing decision-maker keywords (CEO, CTO, CFO, VP, Director, Head of, Managing Director, GM) |
| **Email Dark** | Emails sent but no opens or clicks in 5+ days | Last email send > 5 days ago with no subsequent open/click activity |

Severity levels:

| Severity | Criteria |
|---|---|
| **CRITICAL** | Ghost > 14 days, OR deal value in top 20% AND any diagnosis |
| **HIGH** | Ghost 7-14 days, OR multiple diagnosis categories on one deal |
| **MEDIUM** | Single-threaded OR No DM (alone) |
| **LOW** | Email Dark (alone, < 7 days) |

## Execution

### Step 1: Pull all open deals with activity data

Use `query_crm_data`:

```sql
SELECT hs_object_id, dealname, dealstage, amount, deal_currency_code,
       hubspot_owner_id, pipeline, createdate, closedate,
       hs_lastmodifieddate, notes_last_updated,
       num_associated_contacts, hs_num_associated_contacts
FROM DEAL
WHERE dealstage NOT IN ('closedwon', 'closedlost')
```

Set `chatInsights`:
```json
{
  "userIntent": "diagnose stuck deals and identify pipeline risks",
  "satisfaction": "NEUTRAL"
}
```

### Step 2: Identify Ghost deals

For each open deal, check for recent activity. Use `search_crm_objects` to find deals with no recent notes or modifications:

```json
{
  "objectType": "DEAL",
  "properties": ["hs_object_id", "dealname", "amount", "deal_currency_code", "dealstage", "notes_last_updated", "hs_lastmodifieddate", "hubspot_owner_id"],
  "filterGroups": [{
    "filters": [
      {
        "propertyName": "dealstage",
        "operator": "NOT_IN",
        "values": ["closedwon", "closedlost"]
      },
      {
        "propertyName": "notes_last_updated",
        "operator": "LT",
        "value": "{7_days_ago_timestamp}"
      }
    ]
  }],
  "chatInsights": {
    "userIntent": "diagnose stuck deals and identify pipeline risks",
    "satisfaction": "NEUTRAL"
  }
}
```

Calculate days since last activity: `today - max(notes_last_updated, hs_lastmodifieddate)`.

- 7-14 days silence: **Ghost (HIGH)**
- 14+ days silence: **Ghost (CRITICAL)**

### Step 3: Identify Single-threaded deals

From the Step 1 results, filter deals where `num_associated_contacts <= 1`.

For deals with exactly 1 contact, retrieve the contact to check their role:

```json
{
  "objectType": "CONTACT",
  "properties": ["hs_object_id", "firstname", "lastname", "jobtitle", "email", "hs_lead_status"],
  "filterGroups": [{
    "associatedWith": [{
      "objectType": "deals",
      "operator": "EQUAL",
      "objectIdValues": [DEAL_ID]
    }]
  }],
  "chatInsights": {
    "userIntent": "diagnose stuck deals and identify pipeline risks",
    "satisfaction": "NEUTRAL"
  }
}
```

### Step 4: Identify No DM deals

For deals with contacts (from Step 3 or by pulling associated contacts), check if any contact has a decision-maker title. Decision-maker keywords to match against `jobtitle`:

```
CEO, CTO, CFO, COO, CIO, CISO, VP, Vice President, Director,
Head of, Managing Director, GM, General Manager, Chief,
Founder, Co-Founder, Owner, Partner, Principal, MD
```

If no contact on the deal has a title matching any of these keywords (case-insensitive partial match), flag as **No DM**.

For deals in Proposal or Negotiation stage without a DM, elevate to **HIGH**.

### Step 5: Identify Email Dark deals

Check email engagement by searching for recent email threads related to the deal contacts.

Use `search_threads` from Gmail to look for recent correspondence with each deal's primary contact:

```json
{
  "query": "to:{contact_email} OR from:{contact_email} newer_than:14d",
  "pageSize": 5,
  "view": "THREAD_VIEW_MINIMAL"
}
```

If the most recent email was sent by the AfriShield rep (outbound) more than 5 days ago with no reply thread, flag as **Email Dark**.

- 5-7 days without opens: **Email Dark (LOW)**
- 7+ days without any response: **Email Dark (MEDIUM)**
- If combined with Ghost: escalate to **HIGH**

### Step 6: Compute composite severity

A deal can have multiple diagnoses. Composite severity rules:

1. Any CRITICAL diagnosis makes the deal CRITICAL
2. 2+ HIGH diagnoses: escalate to CRITICAL
3. 2+ MEDIUM diagnoses: escalate to HIGH
4. Deal value in top 20% of pipeline: add one severity level

### Step 7: Prescribe next actions

For each diagnosis, assign a specific action:

| Diagnosis | Prescribed Action |
|---|---|
| **Ghost (7-14d)** | Send a value-add touchpoint (share relevant industry insight or case study). Switch channel -- try calling or LinkedIn if email is dead. |
| **Ghost (14d+)** | Send a breakup email. If no response in 48h, move to nurture sequence and deprioritize. |
| **Single-threaded** | Research the org chart. Ask your contact for an intro to their colleague who handles {relevant function}. Add at least 2 more contacts. |
| **No DM** | Identify the decision maker via LinkedIn or company website. Ask your contact: "Who else needs to be involved in this decision?" |
| **No DM (Proposal+)** | Urgent: you cannot close without a DM. Request a meeting with the economic buyer before sending any revised proposal. |
| **Email Dark (5-7d)** | Resend with a different subject line. Try a shorter, more direct email. Consider a different time of day. |
| **Email Dark (7d+)** | Switch to phone or LinkedIn. Your emails may be going to spam -- verify the contact's email address. |

### Step 8: Output the report

Structure the output as a prioritized list:

```
AFRISHIELD DEAL STAGE ANALYSIS
Generated: {today}
Total open deals analyzed: {count}
Deals with issues: {issue_count} ({percentage}%)

--- CRITICAL ({count}) ---

1. {Deal Name} | {Stage} | ${Amount}
   Owner: {owner_name}
   Diagnoses:
     - Ghost (18 days since last activity) [CRITICAL]
     - Single-threaded (1 contact: {name}, {title}) [MEDIUM]
   Composite severity: CRITICAL
   Priority actions:
     a. Send breakup email today -- if no response in 48h, move to nurture
     b. Before deprioritizing, research org chart and add 2+ contacts
   Last activity: {date} -- {description}

--- HIGH ({count}) ---

2. {Deal Name} | {Stage} | ${Amount}
   ...

--- MEDIUM ({count}) ---

3. {Deal Name} | {Stage} | ${Amount}
   ...

--- SUMMARY ---
Ghost deals: {count} (${total_value} at risk)
Single-threaded: {count}
No Decision Maker: {count}
Email Dark: {count}

Recommended focus: {top 3 actions that would move the most pipeline value}
```

## Notes

- When checking contacts for DM titles, use case-insensitive partial matching. African enterprises may use different title conventions (e.g., "Group Head" is a DM equivalent).
- Ghost detection uses `notes_last_updated` as the primary signal. If this field is null, fall back to `hs_lastmodifieddate`, but flag that note-taking discipline may be lacking.
- For Email Dark, only flag deals where the AfriShield rep sent the last message. If the prospect sent the last message, the deal is not email-dark even if it was a while ago.
- Batch contact lookups: when checking multiple deals for DM presence, pull contacts in batches using `get_crm_objects` with up to 100 IDs per call to avoid rate limits.
- If the user specifies "my deals," resolve their HubSpot owner ID via `search_owners` and filter by `hubspot_owner_id`.
