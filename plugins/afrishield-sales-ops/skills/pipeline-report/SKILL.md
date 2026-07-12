---
name: pipeline-report
description: Generate a pipeline health report from HubSpot CRM -- total value, stage breakdown, win rate, velocity, and risk flags with period-over-period comparison.
---

# Pipeline Health Report

Generate a comprehensive pipeline health report by pulling live deal data from HubSpot CRM. Calculates key metrics, flags at-risk deals, and compares to a prior period.

## Trigger

User asks for a pipeline report, pipeline review, sales health check, or similar.

## Execution

### Step 1: Resolve date boundaries

Set the current reporting period and the comparison period:

- **Current period:** last 30 days (or user-specified range)
- **Prior period:** the 30 days before the current period

Format dates as `YYYY-MM-DD` for HubSpot queries.

### Step 2: Pull all open deals

Use `query_crm_data` to get the full open pipeline:

```sql
SELECT hs_object_id, dealname, dealstage, amount, deal_currency_code,
       pipeline, hubspot_owner_id, createdate, hs_lastmodifieddate,
       notes_last_updated, num_associated_contacts,
       hs_date_entered_qualifiedtobuy, hs_date_entered_presentationscheduled,
       hs_date_entered_decisionmakerboughtin, hs_date_entered_contractsent,
       closedate
FROM DEAL
WHERE dealstage NOT IN ('closedwon', 'closedlost')
```

Set `verbosityLevel` to `LOW` for data-only results.

Set `chatInsights` to:
```json
{
  "userIntent": "generate pipeline health report with metrics and risk flags",
  "satisfaction": "NEUTRAL"
}
```

If the result count exceeds the page limit, paginate by adjusting the query or using `search_crm_objects` with offset.

### Step 3: Pull closed deals for win-rate calculation

Query deals closed in the current period:

```sql
SELECT hs_object_id, dealname, dealstage, amount, deal_currency_code,
       closedate, days_to_close
FROM DEAL
WHERE dealstage IN ('closedwon', 'closedlost')
  AND closedate BETWEEN '{current_period_start}' AND '{current_period_end}'
```

Query deals closed in the prior period (same structure, prior date range).

### Step 4: Pull deal activity timestamps

For each open deal, check recent activity using `search_crm_objects`:

```json
{
  "objectType": "DEAL",
  "properties": ["hs_object_id", "dealname", "notes_last_updated", "hs_lastmodifieddate", "num_associated_contacts", "hubspot_owner_id"],
  "filterGroups": [{
    "filters": [{
      "propertyName": "dealstage",
      "operator": "NOT_IN",
      "values": ["closedwon", "closedlost"]
    }]
  }],
  "sorts": [{"propertyName": "hs_lastmodifieddate", "direction": "DESCENDING"}],
  "limit": 200,
  "chatInsights": {
    "userIntent": "generate pipeline health report with metrics and risk flags",
    "satisfaction": "NEUTRAL"
  }
}
```

### Step 5: Calculate metrics

Compute the following from the retrieved data:

**Pipeline Summary**
- **Total pipeline value:** sum of `amount` for all open deals
- **Deal count:** total number of open deals
- **Average deal size:** total value / deal count
- **Weighted pipeline:** sum of (amount x stage probability) for each deal

**Stage Breakdown**
- Count and total value per stage: Lead, Qualified, Proposal, Negotiation
- Percentage of total pipeline per stage

**Win Rate**
- Current period: Closed Won / (Closed Won + Closed Lost)
- Prior period: same calculation
- Delta: current - prior (flag if negative)

**Velocity**
- Average days to close (from `days_to_close` on closed-won deals)
- Average days in current stage per open deal (today minus the `hs_date_entered_{stage}` timestamp)
- Prior period comparison

### Step 6: Flag risk indicators

Scan every open deal for these risk conditions:

| Risk | Condition | Severity |
|---|---|---|
| **Stuck deal** | Days in current stage > 14 | HIGH if > 21, MEDIUM if > 14 |
| **No recent activity** | `hs_lastmodifieddate` or `notes_last_updated` older than 7 days | HIGH if > 14 days, MEDIUM if > 7 days |
| **Single-threaded** | `num_associated_contacts` <= 1 | MEDIUM |
| **No close date** | `closedate` is null or empty | LOW |
| **Stale proposal** | Stage is Proposal and days in stage > 10 | HIGH |
| **Overdue close** | `closedate` is in the past but deal is still open | HIGH |

### Step 7: Assemble the report

Output a structured report with these sections:

```
AFRISHIELD PIPELINE HEALTH REPORT
Period: {start_date} to {end_date}
Generated: {today}

--- EXECUTIVE SUMMARY ---
Total pipeline: ${total_value} ({deal_count} deals)
Average deal size: ${avg_size}
Win rate: {win_rate}% ({delta} vs prior period)
Avg days to close: {velocity} days

--- STAGE BREAKDOWN ---
| Stage        | Deals | Value       | % of Pipeline | Avg Days in Stage |
|--------------|-------|-------------|---------------|-------------------|
| Lead         | ...   | ...         | ...           | ...               |
| Qualified    | ...   | ...         | ...           | ...               |
| Proposal     | ...   | ...         | ...           | ...               |
| Negotiation  | ...   | ...         | ...           | ...               |

--- WIN/LOSS ANALYSIS ---
Current period: {won} won / {lost} lost ({win_rate}%)
Prior period: {prior_won} won / {prior_lost} lost ({prior_win_rate}%)
Trend: {up/down/flat}

--- RISK FLAGS ---
HIGH: {count} deals
  - {deal_name}: {risk_description}
MEDIUM: {count} deals
  - {deal_name}: {risk_description}

--- TOP DEALS TO WATCH ---
(Top 5 deals by value with their risk status)

--- RECOMMENDED ACTIONS ---
1. {action based on highest-severity risks}
2. {action based on pipeline gaps}
3. {action based on velocity trends}
```

## Notes

- Currency: always include `deal_currency_code` when pulling `amount`. Display in the deal's native currency.
- If the HubSpot portal uses custom deal stages, discover them first with `get_properties` on `DEAL` for the `dealstage` property to get the enumeration values.
- The `hs_date_entered_*` properties are auto-generated by HubSpot for each pipeline stage. Use `search_properties` to find the exact property names if the pipeline has custom stages.
- When the user says "my pipeline," resolve their HubSpot owner ID first using the `search_owners` tool, then filter deals by `hubspot_owner_id`.
