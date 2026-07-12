---
name: weekly-marketing-report
description: "Full GCPS pipeline that gathers data from HubSpot, Gmail, and Google Drive, contextualizes against African market benchmarks, processes revenue/spend/ROAS metrics, and structures a branded visual report with charts."
---

# Weekly Marketing Report

Generate a comprehensive weekly marketing performance report for AfriShield using the GCPS pipeline: Gather, Contextualize, Process, Structure.

---

## Phase 1: GATHER

Collect raw data from all connected sources for the reporting period (default: previous 7 days).

### 1A. HubSpot CRM -- Contacts and Deals

Pull all new contacts created in the period, segmented by lifecycle stage:

```tool
query_crm_data({
  objectType: "contacts",
  filterGroups: [{
    filters: [{
      propertyName: "createdate",
      operator: "BETWEEN",
      value: "<period_start_iso>",
      highValue: "<period_end_iso>"
    }]
  }],
  properties: ["firstname", "lastname", "email", "lifecyclestage", "hs_lead_status", "hs_analytics_source", "createdate", "company"],
  limit: 200
})
```

Pull all deals updated in the period with pipeline and stage data:

```tool
query_crm_data({
  objectType: "deals",
  filterGroups: [{
    filters: [{
      propertyName: "hs_lastmodifieddate",
      operator: "BETWEEN",
      value: "<period_start_iso>",
      highValue: "<period_end_iso>"
    }]
  }],
  properties: ["dealname", "amount", "dealstage", "pipeline", "closedate", "hs_analytics_source", "hubspot_owner_id", "deal_currency_code"],
  limit: 200
})
```

Pull all deals that closed as won in the period:

```tool
query_crm_data({
  objectType: "deals",
  filterGroups: [{
    filters: [
      { propertyName: "dealstage", operator: "EQ", value: "closedwon" },
      { propertyName: "closedate", operator: "BETWEEN", value: "<period_start_iso>", highValue: "<period_end_iso>" }
    ]
  }],
  properties: ["dealname", "amount", "pipeline", "hs_analytics_source", "closedate", "deal_currency_code"],
  limit: 200
})
```

### 1B. HubSpot CRM -- Campaign Performance

Retrieve active campaigns and their engagement metrics:

```tool
get_crm_objects({
  objectType: "campaigns",
  properties: ["hs_campaign_name", "hs_campaign_status", "hs_campaign_start_date", "hs_campaign_end_date", "hs_campaign_budget"]
})
```

For each active campaign, pull associated contacts:

```tool
get_campaign_contacts_by_type({
  campaignId: "<campaign_id>",
  contactType: "all"
})
```

Pull campaign asset metrics (emails, landing pages, CTAs):

```tool
get_campaign_asset_metrics({
  campaignId: "<campaign_id>"
})
```

Pull campaign analytics for the period:

```tool
get_campaign_analytics({
  campaignId: "<campaign_id>",
  startDate: "<period_start_iso>",
  endDate: "<period_end_iso>"
})
```

### 1C. Gmail -- Ad Receipts and Spend Data

Search Gmail for ad platform receipts to capture actual spend:

```tool
search_threads({
  query: "from:(ads-noreply@google.com OR noreply@facebookmail.com OR ads@linkedin.com OR billing@twitter.com OR noreply@tiktok.com) subject:(receipt OR invoice OR charge OR payment) after:<period_start_yyyy/mm/dd> before:<period_end_yyyy/mm/dd>"
})
```

For each matching thread, extract the message body:

```tool
get_thread({ threadId: "<thread_id>" })
```

Parse each receipt for: platform name, amount charged, currency, billing period, campaign name (if present).

Search for marketing vendor invoices:

```tool
search_threads({
  query: "subject:(invoice OR receipt) (marketing OR campaign OR ads OR SEO OR content) after:<period_start_yyyy/mm/dd> before:<period_end_yyyy/mm/dd>"
})
```

### 1D. HubSpot CRM -- Revenue Line Segmentation

Pull deals segmented by each revenue line using pipeline or custom property filters:

**Consumer revenue:**
```tool
search_crm_objects({
  objectType: "deals",
  filterGroups: [{
    filters: [
      { propertyName: "pipeline", operator: "EQ", value: "consumer" },
      { propertyName: "closedate", operator: "BETWEEN", value: "<period_start_iso>", highValue: "<period_end_iso>" }
    ]
  }],
  properties: ["dealname", "amount", "dealstage", "hs_analytics_source"]
})
```

**B2B Cyber revenue:**
```tool
search_crm_objects({
  objectType: "deals",
  filterGroups: [{
    filters: [
      { propertyName: "pipeline", operator: "EQ", value: "b2b_cyber" },
      { propertyName: "closedate", operator: "BETWEEN", value: "<period_start_iso>", highValue: "<period_end_iso>" }
    ]
  }],
  properties: ["dealname", "amount", "dealstage", "hs_analytics_source"]
})
```

**AI SEO revenue:**
```tool
search_crm_objects({
  objectType: "deals",
  filterGroups: [{
    filters: [
      { propertyName: "pipeline", operator: "EQ", value: "ai_seo" },
      { propertyName: "closedate", operator: "BETWEEN", value: "<period_start_iso>", highValue: "<period_end_iso>" }
    ]
  }],
  properties: ["dealname", "amount", "dealstage", "hs_analytics_source"]
})
```

**EA Services revenue:**
```tool
search_crm_objects({
  objectType: "deals",
  filterGroups: [{
    filters: [
      { propertyName: "pipeline", operator: "EQ", value: "ea_services" },
      { propertyName: "closedate", operator: "BETWEEN", value: "<period_start_iso>", highValue: "<period_end_iso>" }
    ]
  }],
  properties: ["dealname", "amount", "dealstage", "hs_analytics_source"]
})
```

---

## Phase 2: CONTEXTUALIZE

Benchmark gathered data against African fraud-detection market context and prior performance.

### 2A. Prior Period Comparison

Re-run all Phase 1 queries with date ranges shifted back by one period (previous week) and by four periods (same week last month) to compute:

- **Week-over-week (WoW) change** for every metric
- **Month-over-month (MoM) trend** for every metric
- **4-week moving average** to smooth volatility

### 2B. African Market Benchmarks

Apply these industry benchmarks for cybersecurity and fraud detection in African markets:

| Metric | African Cybersec Benchmark | Source Context |
|--------|---------------------------|----------------|
| Average CAC (B2B) | $120-$280 USD | Enterprise SaaS in SSA markets |
| Average CAC (Consumer) | $8-$25 USD | Mobile-first consumer security |
| Email open rate | 18-24% | African B2B tech sector |
| Email click rate | 2.5-4.2% | African B2B tech sector |
| Landing page conversion | 2.8-5.5% | Cybersecurity vertical |
| Sales cycle (B2B) | 45-90 days | Enterprise deals in Africa |
| Sales cycle (Consumer) | 1-7 days | Mobile app / freemium |
| Churn rate (B2B) | 3-7% monthly | SaaS in emerging markets |
| Churn rate (Consumer) | 8-15% monthly | Consumer security apps |
| ROAS target (Paid) | 3.0x-5.0x | Digital ads in SSA |
| ROAS target (Organic) | 8.0x-15.0x | Content/SEO long-term |

Flag any metric that falls below the low end of its benchmark range as a warning. Flag any metric exceeding the high end as an outperformance highlight.

### 2C. Seasonal and Regional Context

Note any relevant context for the period:
- Public holidays in target African markets (Nigeria, Kenya, South Africa, Ghana, Egypt)
- Major cybersecurity events or breaches in Africa during the period
- Regulatory changes affecting fintech/cybersecurity in target countries
- Currency fluctuations for NGN, KES, ZAR, GHS, EGP against USD

---

## Phase 3: PROCESS

Calculate derived metrics from gathered and contextualized data.

### 3A. Revenue by Line

For each of the 4 revenue lines (Consumer, B2B Cyber, AI SEO, EA Services), compute:

- **Total revenue:** Sum of closed-won deal amounts
- **Pipeline value:** Sum of open deal amounts
- **Win rate:** Closed-won deals / (Closed-won + Closed-lost) as percentage
- **Average deal size:** Total revenue / Number of closed-won deals
- **Revenue velocity:** Pipeline value * Win rate / Average sales cycle length

### 3B. Spend by Channel

Categorize all marketing spend into the 5 channels:

| Channel | Spend Sources |
|---------|---------------|
| **Paid Ads** | Google Ads receipts, Facebook/Meta Ads receipts, LinkedIn Ads receipts, TikTok Ads receipts, Twitter/X Ads receipts |
| **Organic** | SEO tool subscriptions, content creation costs (freelancer invoices), social media management tools |
| **Email** | HubSpot email sending costs, email template/design costs |
| **Referral** | Referral program payouts, affiliate commissions |
| **Partner** | Co-marketing costs, partner event sponsorships, channel partner incentives |

Sum spend for each channel from Gmail receipts and invoice data.

### 3C. ROAS per Channel

For each of the 5 channels, calculate:

```
ROAS = Revenue attributed to channel / Spend on channel
```

Attribution model: Use `hs_analytics_source` from HubSpot deals to map revenue to channels:
- `PAID_SEARCH`, `PAID_SOCIAL` -> Paid Ads
- `ORGANIC_SEARCH`, `ORGANIC_SOCIAL`, `DIRECT_TRAFFIC` -> Organic
- `EMAIL_MARKETING` -> Email
- `REFERRALS` -> Referral
- `OTHER_CAMPAIGNS` -> Partner

### 3D. Derived Metrics

Compute the following for each channel and in aggregate:

| Metric | Formula |
|--------|---------|
| **CAC (Customer Acquisition Cost)** | Total marketing spend for channel / New customers acquired via channel |
| **LTV (Lifetime Value)** | Average revenue per customer * Average customer lifespan (months) * (1 - monthly churn rate) |
| **LTV:CAC Ratio** | LTV / CAC (target: >3.0x) |
| **Conversion Rate** | Customers / Leads per channel |
| **Cost per Lead (CPL)** | Channel spend / Leads generated |
| **Cost per MQL** | Channel spend / MQLs generated |
| **MQL-to-SQL Rate** | SQLs / MQLs per channel |
| **SQL-to-Close Rate** | Closed-won / SQLs per channel |
| **Payback Period** | CAC / (Monthly revenue per customer) in months |

### 3E. Anomaly Detection

Flag any metric that shows:
- Greater than 20% WoW deviation (positive or negative)
- Greater than 2 standard deviations from the 4-week moving average
- A channel with ROAS below 1.0x (spending more than earning)
- CAC exceeding the upper benchmark threshold
- Conversion rate drops of more than 30% WoW

---

## Phase 4: STRUCTURE

Output the final branded report using AfriShield visual identity.

### 4A. Report Header

Use show_widget to render a branded header:

- AfriShield logo area with brand colors (primary: `#0F7248`, dark: `#073F27`, light: `#EAF7F1`)
- Report title in **Sora** font: "Weekly Marketing Performance Report"
- Subtitle in **Inter** font: reporting period dates
- Generation timestamp

### 4B. Executive Summary Widget

Render a summary dashboard with show_widget containing:

- **4 KPI cards** (one per revenue line) showing total revenue, WoW change, and trend arrow
- **Overall ROAS** as a large metric with benchmark comparison
- **Total spend** vs. **Total revenue** with net margin
- **Top performing channel** and **underperforming channel** callouts
- Color-code: green (`#0F7248`) for metrics at/above benchmark, amber for within 10% of benchmark floor, red for below benchmark

### 4C. Channel Performance Bar Chart

Render a grouped bar chart with show_widget:

- X-axis: 5 marketing channels (Paid Ads, Organic, Email, Referral, Partner)
- Y-axis (left): Revenue attributed (bars in `#0F7248`)
- Y-axis (right): Spend (bars in `#073F27`)
- Overlay line: ROAS per channel
- Include WoW change labels on each bar
- Background: `#EAF7F1`

### 4D. Revenue Mix Pie Chart

Render a donut chart with show_widget:

- 4 segments: Consumer, B2B Cyber, AI SEO, EA Services
- Color palette derived from brand greens: `#0F7248`, `#073F27`, `#1A9B62`, `#EAF7F1`
- Center label: Total revenue figure
- Each segment labeled with percentage and absolute value

### 4E. Cost Breakdown Pie Chart

Render a donut chart with show_widget:

- 5 segments: Paid Ads, Organic, Email, Referral, Partner
- Same brand color palette
- Center label: Total spend figure
- Highlight the highest-spend channel

### 4F. Metrics Table

Render a styled table with show_widget containing all derived metrics from Phase 3D:

- Rows: One per channel plus an "Aggregate" row
- Columns: CAC, LTV, LTV:CAC, Conversion Rate, CPL, MQL-to-SQL, SQL-to-Close, ROAS, Payback Period
- Conditional formatting: green/amber/red based on benchmark thresholds
- Font: Inter for all table content

### 4G. Recommendations Section

Based on the processed data, generate an actionable recommendations section:

1. **Channels to scale:** Any channel with ROAS above 5.0x and positive WoW trend
2. **Channels to optimize:** Any channel with ROAS between 1.0x and 3.0x
3. **Channels to cut or pause:** Any channel with ROAS below 1.0x for 2+ consecutive weeks
4. **Budget reallocation suggestion:** Propose shifting spend from lowest-ROAS to highest-ROAS channel, with projected impact
5. **Quick wins:** Identify the highest-leverage improvements (e.g., landing page with high traffic but low conversion)

### 4H. Anomaly Alerts

List all anomalies detected in Phase 3E as a styled alert box:
- Red alerts for negative anomalies (ROAS drops, CAC spikes)
- Green alerts for positive anomalies (conversion rate jumps, cost decreases)
- Each alert includes the metric name, current value, expected range, and suggested action
