# AfriShield Sales Ops Plugin

Sales operations toolkit for AfriShield. Provides pipeline analytics, branded sales decks, stuck-deal diagnosis, and follow-up automation -- all wired to HubSpot CRM and Gmail.

**Inherits from:** `afrishield-core` (brand reference, data spine, deck generator)

## Company

**AfriShield** delivers cybersecurity, fraud detection, AI SEO, and EA (Enterprise Advisory) services purpose-built for African markets. Revenue lines: Consumer, B2B Cyber, AI SEO, EA Services.

## Connected Tools

| Tool | Purpose |
|---|---|
| HubSpot CRM | Deal pipeline, contacts, companies, activity history |
| Gmail | Email engagement tracking, draft creation for follow-ups |
| Google Calendar | Meeting context for deal activity |
| Firecrawl | Prospect and competitor enrichment |

## Deal Stages (HubSpot)

Lead > Qualified > Proposal > Negotiation > Closed Won > Closed Lost

## Skills

| Skill | Purpose |
|---|---|
| `pipeline-report` | Pipeline health report with metrics, risk flags, and period-over-period comparison. |
| `pipeline-deck` | Branded 9-slide PowerPoint pipeline presentation using pptxgenjs with AfriShield visual identity. |
| `deal-stage-analysis` | Diagnose stuck deals -- Ghost, Single-threaded, No DM, Email Dark -- with severity and prescribed actions. |
| `follow-up-tracker` | Scan CRM for follow-up candidates, prioritize by urgency, draft personalized emails via Gmail. |

## Architecture

```
afrishield-sales-ops/
  plugin.md                          <-- you are here
  skills/
    pipeline-report/
      SKILL.md                       <-- pipeline health analytics
    pipeline-deck/
      SKILL.md                       <-- branded pptx deck
    deal-stage-analysis/
      SKILL.md                       <-- stuck deal diagnosis
    follow-up-tracker/
      SKILL.md                       <-- follow-up automation
```

## Design Principles

1. **Inherit, don't duplicate.** Brand colors, fonts, and voice come from afrishield-core/brand-reference. This plugin consumes them.
2. **CRM is the source of truth.** All deal data comes from HubSpot via query_crm_data and search_crm_objects. No manual spreadsheets.
3. **Action-oriented outputs.** Every report ends with concrete next steps. Every risk flag has a prescribed action.
4. **African market context.** Deal velocity benchmarks, currency handling, and timezone awareness are calibrated for African enterprise sales cycles.
