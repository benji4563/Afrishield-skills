---
name: brand-reference
description: "READ-ONLY AfriShield brand system reference. Contains the canonical color palette, typography stack, voice and tone rules, logo specifications, and usage guidelines. Other skills import this file as their source of truth -- never modify it directly."
---

# AfriShield Brand Reference

> This is a LOCKED reference document. Do not modify. All AfriShield skills must conform to these specifications.

---

## 1. Color Palette

### Primary Green Scale

| Token | Hex | Usage |
|---|---|---|
| G50 | #EAF7F1 | Light backgrounds, card fills, hover states |
| G100 | #C7EBDA | Secondary backgrounds, borders, dividers |
| G300 | #5CBE91 | Accent elements, progress bars, secondary buttons |
| G600 | #0F7248 | **Primary brand color.** Buttons, headers, links, key UI elements |
| G800 | #073F27 | Dark accents, footer backgrounds, emphasized text on light |
| G900 | #04271A | Deepest dark backgrounds, overlay panels |

### Neutrals

| Token | Hex | Usage |
|---|---|---|
| Neutral-900 | #14140F | Primary body text, headings on light backgrounds |
| Neutral-100 | #F4F3EE | Page backgrounds, light-mode canvas, card backgrounds |

### Semantic Colors (derived)

| Purpose | Light mode | Dark mode |
|---|---|---|
| Success | G600 #0F7248 | G300 #5CBE91 |
| Warning | #D4A017 | #F5C842 |
| Error | #C0392B | #E74C3C |
| Info | G600 #0F7248 | G100 #C7EBDA |

### Color Rules

- Primary actions always use G600.
- Never use pure black (#000000); use Neutral-900 instead.
- Never use pure white (#FFFFFF); use Neutral-100 instead.
- Dark backgrounds use G900 or G800; light backgrounds use G50 or Neutral-100.
- G300 is for accents only, never for primary text or large background fills.
- Minimum contrast ratio: 4.5:1 for body text, 3:1 for large text and UI elements.

---

## 2. Typography

### Font Stack

| Role | Web/Digital | PowerPoint (mapped) | Fallback |
|---|---|---|---|
| Headings | Sora | Calibri Bold | Arial Bold, sans-serif |
| Body | Inter | Calibri | Arial, sans-serif |
| Code/Data | JetBrains Mono | Consolas | Courier New, monospace |

### Type Scale

| Level | Size (pt) | Weight | Font | Line Height |
|---|---|---|---|---|
| H1 | 36 | 700 (Bold) | Sora / Calibri Bold | 1.2 |
| H2 | 28 | 600 (SemiBold) | Sora / Calibri Bold | 1.25 |
| H3 | 22 | 600 (SemiBold) | Sora / Calibri Bold | 1.3 |
| Body Large | 18 | 400 (Regular) | Inter / Calibri | 1.5 |
| Body | 14 | 400 (Regular) | Inter / Calibri | 1.6 |
| Caption | 12 | 400 (Regular) | Inter / Calibri | 1.4 |
| Code | 13 | 400 (Regular) | JetBrains Mono / Consolas | 1.5 |

### Typography Rules

- Headings are always Sora (Calibri Bold in PowerPoint). Never use Inter for headings.
- Body text is always Inter (Calibri in PowerPoint). Never use Sora for body paragraphs.
- Data tables, code snippets, and metric callouts use JetBrains Mono (Consolas in PowerPoint).
- Maximum two font sizes per slide or content block.
- Minimum body text size: 14pt digital, 16pt projected/presentation.

---

## 3. Logo Specifications

### Signal Node Logo

The AfriShield logo is the **Signal Node** -- a stylized network node emitting protective signal waves, representing invisible digital protection radiating outward.

**Construction:**
- Central node: circle filled with G600 (#0F7248)
- Signal arcs: three concentric quarter-arcs radiating from the node, progressively lighter (G600, G300, G100)
- The arcs suggest broadcast, coverage, and layered defense

**Clear Space:**
- Minimum clear space around the logo equals the diameter of the central node on all sides.

**Minimum Size:**
- Digital: 32px height minimum
- Print: 12mm height minimum

**Placement:**
- Slide decks: bottom-right of every slide, or top-left of title slides
- Documents: top-left header
- Email signatures: left-aligned, 40px height

**Color Variations:**
- Full color: G600 node + G300/G100 arcs on Neutral-100 or white background
- Reversed: Neutral-100 node + G100/G300 arcs on G900 or G800 background
- Monochrome: all elements in Neutral-900 (for fax, single-color print)

**Prohibited Uses:**
- Never rotate the logo
- Never change the arc colors independently
- Never place on busy photographic backgrounds without a solid backing panel
- Never stretch or distort the aspect ratio

---

## 4. Voice and Tone

### Voice Adjectives

AfriShield's voice is defined by four pillars:

1. **Authoritative** -- We speak from deep expertise. We have the data, the track record, and the technical depth. We do not hedge unnecessarily or qualify every statement.
2. **Warm** -- We are human, approachable, and invested in our clients' success. African markets deserve partners, not vendors. We use "we" and "your" naturally.
3. **Clear** -- We eliminate jargon unless the audience is technical. One idea per sentence. Short paragraphs. Active voice. If a simpler word exists, use it.
4. **Bold** -- We make definitive recommendations. We name risks directly. We do not hide behind passive constructions or weasel words.

### Tone Shifts by Context

| Context | Lean toward | Dial back |
|---|---|---|
| Sales deck | Bold, Warm | -- |
| Technical report | Authoritative, Clear | Warm (slightly) |
| Incident response | Authoritative, Clear | Bold (avoid alarm) |
| Blog / thought leadership | Warm, Bold | -- |
| Internal memo | Clear, Authoritative | Warm (keep professional) |
| Customer email | Warm, Clear | Bold (keep collaborative) |

### Do / Don't Examples

**DO:**
- "AfriShield detected 14,000 fraud attempts across your payment endpoints last quarter. Here is what we recommend."
- "Your exposure in the mobile money channel has grown 3x. We need to talk about rate-limiting."
- "We built this for the realities of African infrastructure -- intermittent connectivity, multi-currency flows, regulatory fragmentation."

**DON'T:**
- "It has come to our attention that there may potentially be some issues with certain aspects of your security posture." (hedging, passive, vague)
- "URGENT: YOUR SYSTEMS ARE AT RISK!!!" (alarmist, unprofessional)
- "Leveraging our best-in-class, enterprise-grade, next-generation solution stack..." (empty jargon)
- "As per our previous correspondence regarding the aforementioned matter..." (bureaucratic)

### Tagline

> "The protection your customers never see you add -- until it saves them"

Use the tagline on:
- Title slides of external decks
- Website hero sections
- Email signature blocks (optional)
- Marketing collateral footers

Never modify the tagline. Never paraphrase it in contexts where the exact tagline is expected.

---

## 5. Revenue Line Naming

Always use these exact names in reports and presentations:

| Internal code | Display name | Description |
|---|---|---|
| consumer | Consumer | Direct-to-consumer fraud protection and identity services |
| b2b_cyber | B2B Cyber | Enterprise cybersecurity solutions for African businesses |
| ai_seo | AI SEO | AI-powered search engine optimization and content strategy |
| ea_services | EA Services | Enterprise Advisory -- strategic consulting and implementation |

---

## 6. Imagery and Iconography Guidelines

- Prefer abstract geometric patterns over stock photography.
- When human imagery is used, it must authentically represent African professionals and markets.
- Icon style: outlined, 2px stroke, rounded corners, using G600 on light or G100 on dark.
- Data visualizations use the green scale (G100 through G800) with Neutral-900 for labels.
- Charts: primary series in G600, secondary in G300, tertiary in G800, quaternary in G100.

---

## 7. File Naming Conventions

- Decks: `afrishield-[topic]-[audience]-[YYYY-MM-DD].pptx`
- Reports: `afrishield-[report-type]-[period].pdf`
- Data exports: `afrishield-[data-type]-[YYYY-MM-DD].csv`

---

*This brand reference is maintained by the AfriShield brand team. Last updated: 2026-07-12. Version: 1.0.0*
