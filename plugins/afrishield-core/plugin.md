# AfriShield Core Plugin

The foundational plugin for AfriShield operations. Provides branded content generation, competitive intelligence gathering, CRM data orchestration, and a locked brand reference system.

## Company

**AfriShield** delivers cybersecurity, fraud detection, AI SEO, and EA (Enterprise Advisory) services purpose-built for African markets. Revenue lines: Consumer, B2B Cyber, AI SEO, EA Services.

**Tagline:** "The protection your customers never see you add -- until it saves them"

## Skills

| Skill | Purpose |
|---|---|
| `branded-deck` | Generate branded PowerPoint decks using pptxgenjs with AfriShield's full visual identity -- G600 green, dark/light sandwich layouts, Calibri font mapping, Signal Node logo. |
| `data-scraper` | Firecrawl-powered web intelligence -- competitor analysis, market sizing, prospect enrichment for African cybersecurity and fintech markets. |
| `weekly-report-organizer` | HubSpot CRM data spine that pulls deals, contacts, and companies into a standard model consumed by pipeline, marketing, and sales reports. |
| `brand-reference` | READ-ONLY brand system. Colors, typography, voice, tone, logo specs. Other skills import this; never modify it directly. |

## Architecture

```
afrishield-core/
  plugin.md              <-- you are here
  skills/
    branded-deck/
      SKILL.md           <-- pptxgenjs deck generator
    data-scraper/
      SKILL.md           <-- Firecrawl web intelligence
    weekly-report-organizer/
      SKILL.md           <-- HubSpot data spine
    brand-reference/
      SKILL.md           <-- locked brand system
```

## Design Principles

1. **Brand-first.** Every customer-facing output uses the locked brand reference. No ad-hoc colors or fonts.
2. **Data spine pattern.** The weekly-report-organizer pulls raw CRM data once; downstream skills consume the structured output rather than making their own HubSpot queries.
3. **African market context.** Search queries, competitor lists, and market assumptions are calibrated for Sub-Saharan Africa, North Africa, and pan-African markets.
4. **Reproducibility.** Decks, reports, and analyses are deterministic given the same inputs. Templates define structure; data fills slots.
