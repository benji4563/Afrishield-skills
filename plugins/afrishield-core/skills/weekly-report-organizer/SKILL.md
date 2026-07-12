---
name: weekly-report-organizer
description: "HubSpot CRM data spine for AfriShield. Pulls deals, contacts, and companies from HubSpot, structures them into a standard data model, and produces the canonical weekly dataset that pipeline, marketing, and sales reports consume."
---

# AfriShield Weekly Report Organizer

This skill is the **data spine** for all AfriShield reporting. It queries HubSpot CRM once, structures the data into a standard model, and produces outputs that downstream skills (branded-deck, dashboards, email summaries) consume directly. No other skill should query HubSpot independently -- they read the structured output from this skill.

---

## Tools Used

| Tool | Purpose |
|---|---|
| `get_crm_objects` | Fetch lists of deals, contacts, or companies with specific properties |
| `query_crm_data` | Run filtered queries against CRM data with date ranges and conditions |
| `search_crm_objects` | Search CRM objects by field values, keywords, or complex filters |
| `get_properties` | Discover available properties on CRM object types |
| `search_properties` | Find specific property names when the exact field name is unknown |
| `search_owners` | Look up HubSpot owners (sales reps) by name or email |
| `get_campaign_analytics` | Pull marketing campaign performance data |
| `get_campaign_contacts_by_type` | Get contacts associated with campaigns by engagement type |

---

## Standard Data Model

All downstream consumers expect data in this shape. The weekly-report-organizer produces these structures.

### Deals Dataset

```json
{
  "deals": [
    {
      "id": "string",
      "name": "string",
      "stage": "string",
      "pipeline": "string",
      "amount": "number",
      "currency": "string",
      "close_date": "string (ISO 8601)",
      "create_date": "string (ISO 8601)",
      "owner_name": "string",
      "owner_email": "string",
      "company_name": "string",
      "company_id": "string",
      "revenue_line": "consumer | b2b_cyber | ai_seo | ea_services",
      "country": "string",
      "region": "string (West Africa | East Africa | Southern Africa | North Africa | Pan-Africa)",
      "days_in_stage": "number",
      "last_activity_date": "string (ISO 8601)",
      "next_step": "string"
    }
  ],
  "summary": {
    "total_pipeline_value": "number",
    "weighted_pipeline_value": "number",
    "deals_by_stage": { "stage_name": "count" },
    "deals_by_revenue_line": { "line_name": "count" },
    "deals_by_region": { "region_name": "count" },
    "avg_days_in_pipeline": "number",
    "deals_created_this_week": "number",
    "deals_closed_won_this_week": "number",
    "deals_closed_lost_this_week": "number"
  },
  "period": {
    "start": "string (ISO 8601)",
    "end": "string (ISO 8601)",
    "generated_at": "string (ISO 8601)"
  }
}
```

### Contacts Dataset

```json
{
  "contacts": [
    {
      "id": "string",
      "first_name": "string",
      "last_name": "string",
      "email": "string",
      "company_name": "string",
      "company_id": "string",
      "job_title": "string",
      "lifecycle_stage": "string",
      "lead_status": "string",
      "owner_name": "string",
      "create_date": "string (ISO 8601)",
      "last_activity_date": "string (ISO 8601)",
      "source": "string",
      "country": "string"
    }
  ],
  "summary": {
    "total_contacts": "number",
    "new_contacts_this_week": "number",
    "contacts_by_lifecycle_stage": {},
    "contacts_by_source": {},
    "contacts_by_country": {},
    "mqls_this_week": "number",
    "sqls_this_week": "number"
  }
}
```

### Companies Dataset

```json
{
  "companies": [
    {
      "id": "string",
      "name": "string",
      "domain": "string",
      "industry": "string",
      "country": "string",
      "region": "string",
      "employee_count": "string",
      "annual_revenue": "string",
      "owner_name": "string",
      "associated_deals_count": "number",
      "total_deal_value": "number",
      "create_date": "string (ISO 8601)",
      "last_activity_date": "string (ISO 8601)"
    }
  ],
  "summary": {
    "total_companies": "number",
    "new_companies_this_week": "number",
    "companies_by_industry": {},
    "companies_by_region": {},
    "companies_with_active_deals": "number"
  }
}
```

---

## Data Collection Procedure

Execute these steps in order every time the weekly report is requested.

### Step 1: Discover Properties

Before the first run (or if properties are unknown), discover available properties:

```
get_properties({ objectType: "deals" })
get_properties({ objectType: "contacts" })
get_properties({ objectType: "companies" })
```

Use `search_properties` if you need to find the exact property name for a concept:

```
search_properties({ objectType: "deals", query: "revenue line" })
search_properties({ objectType: "deals", query: "country" })
search_properties({ objectType: "deals", query: "region" })
```

### Step 2: Resolve Owners

```
search_owners({ query: "" })
```

This returns all owners. Build a lookup map of owner ID to name/email for enriching deal and contact records.

### Step 3: Pull Deals

Fetch all deals with relevant properties:

```
get_crm_objects({
  objectType: "deals",
  properties: [
    "dealname", "dealstage", "pipeline", "amount",
    "closedate", "createdate", "hubspot_owner_id",
    "hs_lastmodifieddate", "hs_next_step",
    "revenue_line", "country", "region"
  ],
  limit: 100
})
```

For deals created or modified this week:

```
query_crm_data({
  objectType: "deals",
  filters: [
    {
      propertyName: "hs_lastmodifieddate",
      operator: "GTE",
      value: "[MONDAY_OF_THIS_WEEK_ISO]"
    }
  ],
  properties: [
    "dealname", "dealstage", "pipeline", "amount",
    "closedate", "createdate", "hubspot_owner_id",
    "hs_lastmodifieddate", "hs_next_step",
    "revenue_line", "country", "region"
  ]
})
```

For closed-won deals this week:

```
search_crm_objects({
  objectType: "deals",
  searchTerm: "",
  filters: [
    {
      propertyName: "dealstage",
      operator: "EQ",
      value: "closedwon"
    },
    {
      propertyName: "closedate",
      operator: "GTE",
      value: "[MONDAY_OF_THIS_WEEK_ISO]"
    }
  ],
  properties: ["dealname", "amount", "pipeline", "hubspot_owner_id", "revenue_line", "country"]
})
```

### Step 4: Pull Contacts

New contacts this week:

```
query_crm_data({
  objectType: "contacts",
  filters: [
    {
      propertyName: "createdate",
      operator: "GTE",
      value: "[MONDAY_OF_THIS_WEEK_ISO]"
    }
  ],
  properties: [
    "firstname", "lastname", "email", "company",
    "jobtitle", "lifecyclestage", "hs_lead_status",
    "hubspot_owner_id", "createdate",
    "hs_analytics_source", "country"
  ]
})
```

MQLs generated this week:

```
search_crm_objects({
  objectType: "contacts",
  filters: [
    {
      propertyName: "lifecyclestage",
      operator: "EQ",
      value: "marketingqualifiedlead"
    },
    {
      propertyName: "hs_lifecyclestage_marketingqualifiedlead_date",
      operator: "GTE",
      value: "[MONDAY_OF_THIS_WEEK_ISO]"
    }
  ],
  properties: ["firstname", "lastname", "email", "company", "hs_analytics_source", "country"]
})
```

### Step 5: Pull Companies

Active companies (with recent activity):

```
query_crm_data({
  objectType: "companies",
  filters: [
    {
      propertyName: "notes_last_updated",
      operator: "GTE",
      value: "[MONDAY_OF_THIS_WEEK_ISO]"
    }
  ],
  properties: [
    "name", "domain", "industry", "country",
    "numberofemployees", "annualrevenue",
    "hubspot_owner_id", "createdate",
    "notes_last_updated", "num_associated_deals"
  ]
})
```

### Step 6: Pull Marketing Data

```
get_campaign_analytics({})
```

```
get_campaign_contacts_by_type({
  campaignId: "[ACTIVE_CAMPAIGN_ID]",
  contactType: "CONVERTED"
})
```

### Step 7: Assemble and Compute

1. **Enrich records** -- Replace `hubspot_owner_id` with owner name/email from the Step 2 lookup.
2. **Classify revenue lines** -- If the `revenue_line` property is not set on a deal, infer from the pipeline name or deal name.
3. **Classify regions** -- Map country to region using:
   - West Africa: Nigeria, Ghana, Senegal, Ivory Coast, Sierra Leone, Liberia, Gambia, Guinea, Togo, Benin, Burkina Faso, Mali, Niger, Cape Verde, Guinea-Bissau, Mauritania
   - East Africa: Kenya, Tanzania, Uganda, Rwanda, Ethiopia, Somalia, Djibouti, Eritrea, South Sudan, Burundi, Comoros, Madagascar, Mauritius, Seychelles
   - Southern Africa: South Africa, Botswana, Namibia, Zimbabwe, Zambia, Mozambique, Malawi, Lesotho, Eswatini, Angola
   - North Africa: Egypt, Morocco, Tunisia, Algeria, Libya, Sudan
   - Pan-Africa: multi-country deals or unspecified
4. **Compute summaries** -- Aggregate counts, sums, and averages as defined in the data model.
5. **Calculate stage velocity** -- For each deal, compute `days_in_stage` from the last stage change date.
6. **Flag stale deals** -- Deals with no activity in 14+ days get flagged.

---

## Downstream Report Outputs

The assembled data feeds these specific reports:

### Pipeline Report

Consumed by: Sales leadership, board deck

Fields used: deals (all), summary.total_pipeline_value, summary.weighted_pipeline_value, summary.deals_by_stage, summary.deals_by_revenue_line

Format: Table of deals sorted by stage then amount descending. Summary metrics at top. Stale deals flagged with warning.

### Marketing Report

Consumed by: Marketing team, weekly standup

Fields used: contacts.summary (new contacts, MQLs, SQLs, by source, by country), campaign analytics

Format: Funnel metrics (visitors -> contacts -> MQLs -> SQLs -> opportunities). Source attribution breakdown. Campaign performance table.

### Sales Report

Consumed by: Sales team, weekly standup

Fields used: deals (grouped by owner), contacts (new leads assigned), companies (active accounts)

Format: Per-rep summary table (deals in pipeline, total value, deals closed this week, next steps). New leads assigned. Account activity.

### Executive Summary

Consumed by: CEO, leadership

Fields used: All summaries from all three datasets

Format: Single-page brief with 5 key metrics, week-over-week trends, top wins, top risks, top actions needed.

---

## Date Handling

- **Week definition:** Monday 00:00:00 UTC through Sunday 23:59:59 UTC.
- **"This week"** means the current ISO week. Calculate Monday's date dynamically.
- **ISO 8601 timestamps** for all date fields. HubSpot returns Unix milliseconds -- convert them.
- **Timezone:** All dates normalized to UTC. AfriShield operates across multiple African time zones; UTC is the canonical reference.

### Date Calculation (JavaScript)

```javascript
function getMondayOfThisWeek() {
  const now = new Date();
  const day = now.getUTCDay();
  const diff = day === 0 ? -6 : 1 - day;  // Monday = 1, Sunday = 0
  const monday = new Date(now);
  monday.setUTCDate(now.getUTCDate() + diff);
  monday.setUTCHours(0, 0, 0, 0);
  return monday.toISOString();
}
```

---

## Error Handling

- If `get_crm_objects` returns no results for a query, note it in the summary as "No data for [query description]" rather than failing silently.
- If a property does not exist (404 from `get_properties`), fall back to searching for an alternative property name with `search_properties`.
- If owner lookup fails, use "Unassigned" as the owner name.
- If the HubSpot connection is not authenticated, inform the user that the HubSpot connector needs authorization in their connector settings and list which reports cannot be generated without it.
- Always report the number of records fetched vs. expected to surface potential pagination issues.

---

## Execution Checklist

When the user requests a weekly report:

- [ ] Confirm the reporting period (default: current week, Monday to today)
- [ ] Run Steps 1-7 in order
- [ ] Present the assembled data in the requested format (pipeline / marketing / sales / executive / all)
- [ ] Flag any data quality issues (missing fields, stale deals, unassigned contacts)
- [ ] Offer to generate a branded deck from the data using the `branded-deck` skill
