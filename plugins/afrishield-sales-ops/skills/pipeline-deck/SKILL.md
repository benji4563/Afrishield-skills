---
name: pipeline-deck
description: Generate a branded 9-slide AfriShield pipeline presentation using pptxgenjs with G600 green, dark/light sandwich layout, and Calibri fonts.
---

# Branded Pipeline Deck

Generate a 9-slide PowerPoint presentation summarizing AfriShield's sales pipeline, using the full AfriShield brand identity via pptxgenjs.

## Trigger

User asks for a pipeline deck, pipeline presentation, sales review slides, or board-ready pipeline summary.

## Prerequisites

Run the `pipeline-report` skill first (or pull the same data inline) to have all metrics, stage breakdowns, risk flags, and win/loss numbers available before building slides.

## Brand Reference

Inherited from `afrishield-core/brand-reference`:

| Token | Value | Usage |
|---|---|---|
| G600 | #0F7248 | Primary green -- accents, chart bars, key numbers |
| G800 | #073F27 | Dark green -- dark slide backgrounds |
| G50 | #EAF7F1 | Light green tint -- light slide backgrounds, table alternating rows |
| White | #FFFFFF | Text on dark slides, card backgrounds |
| Dark text | #1A1A1A | Body text on light slides |
| Heading font | Calibri Bold | All slide titles (mapped from Sora) |
| Body font | Calibri | All body text, table cells, labels (mapped from Inter) |

## Slide Structure

Build the deck using pptxgenjs in the workspace. The 9-slide structure uses a **dark/light sandwich** pattern: dark slides bookend the deck and frame section transitions; light slides carry the data.

### Slide 1: Title (DARK)

- Background: G800 (#073F27) solid fill
- Title: "Pipeline Review" in Calibri Bold, 36pt, white, centered vertically at 35% from top
- Subtitle: "{period_label}" in Calibri, 18pt, G50, centered below title
- Bottom accent bar: 0.15" tall rectangle, full width, G600 fill
- Bottom-right: date in Calibri, 11pt, G50

```javascript
let slide1 = pptx.addSlide();
slide1.background = { color: '073F27' };
slide1.addText('Pipeline Review', {
  x: 0.5, y: 1.8, w: 9, h: 1.2,
  fontSize: 36, fontFace: 'Calibri', bold: true, color: 'FFFFFF', align: 'center'
});
slide1.addText(periodLabel, {
  x: 0.5, y: 3.0, w: 9, h: 0.6,
  fontSize: 18, fontFace: 'Calibri', color: 'EAF7F1', align: 'center'
});
slide1.addShape(pptx.shapes.RECTANGLE, {
  x: 0, y: 7.15, w: 10, h: 0.15, fill: { color: '0F7248' }
});
slide1.addText(todayFormatted, {
  x: 7.5, y: 6.8, w: 2, h: 0.3,
  fontSize: 11, fontFace: 'Calibri', color: 'EAF7F1', align: 'right'
});
```

### Slide 2: Executive Summary (LIGHT)

- Background: white
- Title: "Executive Summary" in Calibri Bold, 24pt, G800, top-left with G600 underline bar
- 4-column KPI cards:
  - Total Pipeline Value | Deal Count | Average Deal Size | Win Rate
  - Each card: rounded rectangle with G50 fill, G600 top border (3pt), metric value in Calibri Bold 28pt G800, label in Calibri 12pt dark text
- 2-line trend comparison below cards: current vs prior period with delta arrows

```javascript
let slide2 = pptx.addSlide();
slide2.addText('Executive Summary', {
  x: 0.5, y: 0.3, w: 5, h: 0.5,
  fontSize: 24, fontFace: 'Calibri', bold: true, color: '073F27'
});
slide2.addShape(pptx.shapes.RECTANGLE, {
  x: 0.5, y: 0.85, w: 1.5, h: 0.04, fill: { color: '0F7248' }
});
// KPI cards at y:1.3, each 2.0" wide with 0.25" gap
const kpis = [
  { label: 'Total Pipeline', value: totalPipelineFormatted },
  { label: 'Deal Count', value: String(dealCount) },
  { label: 'Avg Deal Size', value: avgDealSizeFormatted },
  { label: 'Win Rate', value: winRateFormatted }
];
kpis.forEach((kpi, i) => {
  let xPos = 0.5 + i * 2.25;
  slide2.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
    x: xPos, y: 1.3, w: 2.0, h: 1.6,
    fill: { color: 'EAF7F1' }, rectRadius: 0.1,
    line: { color: '0F7248', width: 0, dashType: 'solid' }
  });
  slide2.addShape(pptx.shapes.RECTANGLE, {
    x: xPos, y: 1.3, w: 2.0, h: 0.05, fill: { color: '0F7248' }
  });
  slide2.addText(kpi.value, {
    x: xPos, y: 1.6, w: 2.0, h: 0.8,
    fontSize: 28, fontFace: 'Calibri', bold: true, color: '073F27', align: 'center'
  });
  slide2.addText(kpi.label, {
    x: xPos, y: 2.35, w: 2.0, h: 0.4,
    fontSize: 12, fontFace: 'Calibri', color: '1A1A1A', align: 'center'
  });
});
```

### Slide 3: Pipeline Overview (LIGHT)

- Title: "Pipeline Overview"
- Horizontal stacked bar chart showing total value split by stage
- Below: deal count badges per stage (small rounded rects with count)
- Chart colors: gradient from G800 (Lead) through G600 (Qualified/Proposal) to G50-border (Negotiation)

```javascript
let slide3 = pptx.addSlide();
slide3.addText('Pipeline Overview', { /* title style */ });
slide3.addChart(pptx.charts.BAR, [{
  name: 'Pipeline Value',
  labels: ['Lead', 'Qualified', 'Proposal', 'Negotiation'],
  values: [leadValue, qualifiedValue, proposalValue, negotiationValue]
}], {
  x: 0.5, y: 1.5, w: 9, h: 3.5,
  barDir: 'bar', barGrouping: 'stacked',
  showValue: true, valueFontSize: 11, valueFontFace: 'Calibri',
  catAxisLabelFontFace: 'Calibri', catAxisLabelFontSize: 12,
  chartColors: ['073F27', '0F7248', '1A9E64', 'A8DEC5']
});
```

### Slide 4: Stage Breakdown (LIGHT)

- Title: "Stage Breakdown"
- Funnel visual: 4 horizontal bars of decreasing width, each labeled with stage name, deal count, and value
- Table below with columns: Stage | Deals | Value | % of Pipeline | Avg Days in Stage
- Table styling: header row G600 fill with white text, alternating G50/white rows

```javascript
let slide4 = pptx.addSlide();
slide4.addText('Stage Breakdown', { /* title style */ });
// Funnel bars
const stages = [
  { name: 'Lead', count: leadCount, value: leadValue, width: 8.5 },
  { name: 'Qualified', count: qualCount, value: qualValue, width: 6.5 },
  { name: 'Proposal', count: propCount, value: propValue, width: 4.5 },
  { name: 'Negotiation', count: negCount, value: negValue, width: 2.5 }
];
stages.forEach((s, i) => {
  let xPos = (9 - s.width) / 2 + 0.5;
  slide4.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
    x: xPos, y: 1.3 + i * 0.7, w: s.width, h: 0.55,
    fill: { color: i < 2 ? '0F7248' : 'A8DEC5' }, rectRadius: 0.05
  });
  slide4.addText(`${s.name}  |  ${s.count} deals  |  ${s.value}`, {
    x: xPos, y: 1.3 + i * 0.7, w: s.width, h: 0.55,
    fontSize: 13, fontFace: 'Calibri', bold: true,
    color: i < 2 ? 'FFFFFF' : '073F27', align: 'center', valign: 'middle'
  });
});
// Data table below funnel
let tableRows = [
  [
    { text: 'Stage', options: { bold: true, color: 'FFFFFF', fill: { color: '0F7248' } } },
    { text: 'Deals', options: { bold: true, color: 'FFFFFF', fill: { color: '0F7248' } } },
    { text: 'Value', options: { bold: true, color: 'FFFFFF', fill: { color: '0F7248' } } },
    { text: '% Pipeline', options: { bold: true, color: 'FFFFFF', fill: { color: '0F7248' } } },
    { text: 'Avg Days', options: { bold: true, color: 'FFFFFF', fill: { color: '0F7248' } } }
  ],
  // ...data rows with alternating EAF7F1 / FFFFFF fills
];
slide4.addTable(tableRows, {
  x: 0.5, y: 4.5, w: 9, fontFace: 'Calibri', fontSize: 11,
  border: { type: 'solid', pt: 0.5, color: 'D0D0D0' }
});
```

### Slide 5: Win/Loss Analysis (LIGHT)

- Title: "Win / Loss Analysis"
- Left half: donut chart -- Closed Won vs Closed Lost (G600 and #CC3333)
- Right half: comparison table showing current vs prior period
  - Won count, Lost count, Win rate, Avg deal size of won deals
- Delta arrows (green up / red down) next to each comparison metric

```javascript
let slide5 = pptx.addSlide();
slide5.addText('Win / Loss Analysis', { /* title style */ });
slide5.addChart(pptx.charts.DOUGHNUT, [{
  name: 'Win/Loss',
  labels: ['Closed Won', 'Closed Lost'],
  values: [wonCount, lostCount]
}], {
  x: 0.5, y: 1.5, w: 4, h: 3.5,
  showPercent: true, showTitle: false,
  chartColors: ['0F7248', 'CC3333'],
  dataLabelFontFace: 'Calibri', dataLabelFontSize: 14
});
// Comparison table on right
```

### Slide 6: Velocity Metrics (LIGHT)

- Title: "Velocity Metrics"
- Bar chart: average days in each stage (Lead, Qualified, Proposal, Negotiation)
- KPI callout box: "Average days to close: {X}" in large text
- Trend line or comparison bar for prior period velocity
- Benchmark annotation: "14-day target per stage" as a reference line

```javascript
let slide6 = pptx.addSlide();
slide6.addText('Velocity Metrics', { /* title style */ });
slide6.addChart(pptx.charts.BAR, [{
  name: 'Current Period',
  labels: ['Lead', 'Qualified', 'Proposal', 'Negotiation'],
  values: [leadDays, qualDays, propDays, negDays]
}, {
  name: 'Prior Period',
  labels: ['Lead', 'Qualified', 'Proposal', 'Negotiation'],
  values: [priorLeadDays, priorQualDays, priorPropDays, priorNegDays]
}], {
  x: 0.5, y: 1.5, w: 6, h: 3.5,
  barDir: 'col', barGrouping: 'clustered',
  showValue: true, valueFontFace: 'Calibri',
  chartColors: ['0F7248', 'A8DEC5'],
  catAxisLabelFontFace: 'Calibri'
});
// KPI callout
slide6.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
  x: 7, y: 1.5, w: 2.5, h: 2, fill: { color: 'EAF7F1' }, rectRadius: 0.1
});
slide6.addText('Avg Days\nto Close', {
  x: 7, y: 1.6, w: 2.5, h: 0.6,
  fontSize: 14, fontFace: 'Calibri', color: '073F27', align: 'center'
});
slide6.addText(String(avgDaysToClose), {
  x: 7, y: 2.2, w: 2.5, h: 1,
  fontSize: 42, fontFace: 'Calibri', bold: true, color: '0F7248', align: 'center'
});
```

### Slide 7: Risk Flags (DARK)

- Background: G800
- Title: "Risk Flags" in white
- Risk cards: one per HIGH-severity risk, red left border (#CC3333), white card on dark background
  - Deal name, risk type, days stuck, prescribed action
- Summary counts: HIGH (red badge), MEDIUM (amber badge), LOW (grey badge)

```javascript
let slide7 = pptx.addSlide();
slide7.background = { color: '073F27' };
slide7.addText('Risk Flags', {
  x: 0.5, y: 0.3, w: 5, h: 0.5,
  fontSize: 24, fontFace: 'Calibri', bold: true, color: 'FFFFFF'
});
// Severity badges
const badges = [
  { label: `${highCount} HIGH`, color: 'CC3333' },
  { label: `${medCount} MEDIUM`, color: 'E6A817' },
  { label: `${lowCount} LOW`, color: '888888' }
];
badges.forEach((b, i) => {
  slide7.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
    x: 0.5 + i * 2.5, y: 1.0, w: 2.0, h: 0.45,
    fill: { color: b.color }, rectRadius: 0.2
  });
  slide7.addText(b.label, {
    x: 0.5 + i * 2.5, y: 1.0, w: 2.0, h: 0.45,
    fontSize: 14, fontFace: 'Calibri', bold: true, color: 'FFFFFF', align: 'center'
  });
});
// Risk cards for top HIGH items
highRiskDeals.slice(0, 4).forEach((deal, i) => {
  let yPos = 1.8 + i * 1.2;
  // Red left border
  slide7.addShape(pptx.shapes.RECTANGLE, {
    x: 0.5, y: yPos, w: 0.08, h: 1.0, fill: { color: 'CC3333' }
  });
  // White card
  slide7.addShape(pptx.shapes.RECTANGLE, {
    x: 0.58, y: yPos, w: 8.92, h: 1.0, fill: { color: 'FFFFFF' }
  });
  slide7.addText(deal.name, {
    x: 0.8, y: yPos + 0.05, w: 5, h: 0.35,
    fontSize: 14, fontFace: 'Calibri', bold: true, color: '073F27'
  });
  slide7.addText(`${deal.riskType} | ${deal.daysStuck} days | Action: ${deal.action}`, {
    x: 0.8, y: yPos + 0.4, w: 8.5, h: 0.5,
    fontSize: 11, fontFace: 'Calibri', color: '1A1A1A'
  });
});
```

### Slide 8: Top Deals to Watch (LIGHT)

- Title: "Top Deals to Watch"
- Table: top 8 deals by value
  - Columns: Deal Name | Stage | Value | Owner | Days in Stage | Risk
  - Risk column uses colored dots: green (clear), amber (medium), red (high)
- Header row: G600 fill, white text

```javascript
let slide8 = pptx.addSlide();
slide8.addText('Top Deals to Watch', { /* title style */ });
let dealRows = [
  [
    { text: 'Deal', options: { bold: true, color: 'FFFFFF', fill: { color: '0F7248' }, fontFace: 'Calibri' } },
    { text: 'Stage', options: { bold: true, color: 'FFFFFF', fill: { color: '0F7248' }, fontFace: 'Calibri' } },
    { text: 'Value', options: { bold: true, color: 'FFFFFF', fill: { color: '0F7248' }, fontFace: 'Calibri' } },
    { text: 'Owner', options: { bold: true, color: 'FFFFFF', fill: { color: '0F7248' }, fontFace: 'Calibri' } },
    { text: 'Days', options: { bold: true, color: 'FFFFFF', fill: { color: '0F7248' }, fontFace: 'Calibri' } },
    { text: 'Risk', options: { bold: true, color: 'FFFFFF', fill: { color: '0F7248' }, fontFace: 'Calibri' } }
  ],
  // ...top deals sorted by amount descending, alternating row fills
];
slide8.addTable(dealRows, {
  x: 0.5, y: 1.2, w: 9, fontFace: 'Calibri', fontSize: 11,
  border: { type: 'solid', pt: 0.5, color: 'D0D0D0' },
  colW: [2.8, 1.2, 1.2, 1.5, 0.8, 1.5]
});
```

### Slide 9: Next Steps / Close (DARK)

- Background: G800
- Title: "Next Steps" in white, centered
- 3-4 action items derived from the risk flags and pipeline gaps, each as a numbered block with G600 number badge
- Bottom: G600 accent bar (mirrors Slide 1)
- Contact line: "Questions? Reach the sales ops team" in G50

```javascript
let slide9 = pptx.addSlide();
slide9.background = { color: '073F27' };
slide9.addText('Next Steps', {
  x: 0.5, y: 0.5, w: 9, h: 0.6,
  fontSize: 28, fontFace: 'Calibri', bold: true, color: 'FFFFFF', align: 'center'
});
nextSteps.forEach((step, i) => {
  let yPos = 1.5 + i * 1.2;
  // Number badge
  slide9.addShape(pptx.shapes.OVAL, {
    x: 1.0, y: yPos, w: 0.5, h: 0.5, fill: { color: '0F7248' }
  });
  slide9.addText(String(i + 1), {
    x: 1.0, y: yPos, w: 0.5, h: 0.5,
    fontSize: 18, fontFace: 'Calibri', bold: true, color: 'FFFFFF', align: 'center', valign: 'middle'
  });
  // Step text
  slide9.addText(step, {
    x: 1.8, y: yPos, w: 7, h: 0.5,
    fontSize: 16, fontFace: 'Calibri', color: 'FFFFFF', valign: 'middle'
  });
});
slide9.addShape(pptx.shapes.RECTANGLE, {
  x: 0, y: 7.15, w: 10, h: 0.15, fill: { color: '0F7248' }
});
```

## Deck Generation

Use the workspace bash environment to run the pptxgenjs script:

```bash
cd /tmp && npm init -y && npm install pptxgenjs
node generate-pipeline-deck.js
```

The script should:
1. Import pptxgenjs
2. Create a new presentation with `layout: 'LAYOUT_WIDE'` (13.33" x 7.5")
3. Build all 9 slides using the patterns above, substituting live data
4. Write to `/tmp/AfriShield_Pipeline_Review_{date}.pptx`
5. Copy to the outputs folder for presentation to the user

## Notes

- Always use `LAYOUT_WIDE` (16:9) for modern presentation displays.
- All font references use Calibri (mapped from Sora/Inter per brand guidelines).
- The dark/light sandwich: slides 1, 7, 9 are dark (G800 background); slides 2-6, 8 are light (white background).
- Chart colors always start from G800 and progress through G600 to lighter greens. Never use colors outside the brand palette.
- If deal data is insufficient (< 3 deals), note this on the executive summary slide and collapse the stage breakdown into a simple list.
