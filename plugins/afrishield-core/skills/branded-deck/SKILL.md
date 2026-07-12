---
name: branded-deck
description: "Generate branded PowerPoint presentations for AfriShield using pptxgenjs in Node.js. Implements the full brand system with G600 green primary, dark/light sandwich slide layouts, Signal Node logo reference, and Calibri font mapping from Sora/Inter."
---

# AfriShield Branded Deck Generator

Generate production-quality PowerPoint decks that conform to AfriShield's brand system. Uses pptxgenjs running in the workspace bash environment.

---

## Brand System (Quick Reference)

Import the full spec from `brand-reference`. Key values for deck generation:

### Colors

```javascript
const COLORS = {
  G50:         'EAF7F1',
  G100:        'C7EBDA',
  G300:        '5CBE91',
  G600:        '0F7248',  // PRIMARY
  G800:        '073F27',
  G900:        '04271A',
  NEUTRAL_900: '14140F',
  NEUTRAL_100: 'F4F3EE',
};
```

### Fonts (PowerPoint Mapping)

| Brand font | PPTX font | Usage |
|---|---|---|
| Sora | Calibri | Headings (apply bold: true) |
| Inter | Calibri | Body text (regular weight) |
| JetBrains Mono | Consolas | Code, metrics, data callouts |

### Logo

The Signal Node logo should be placed as a PNG image. Reference path: `./assets/afrishield-logo.png` (provide the logo file to the script, or use a placeholder shape).

---

## Slide Templates

Every AfriShield deck uses the **dark/light sandwich layout**: dark slides bookend the presentation (title + closing), with light content slides in between. Section dividers use dark backgrounds to create visual rhythm.

### Template 1: Title Slide (Dark)

```javascript
function addTitleSlide(pptx, { title, subtitle, date, presenter }) {
  const slide = pptx.addSlide();
  slide.background = { color: COLORS.G900 };

  // Title
  slide.addText(title, {
    x: 0.8, y: 1.5, w: 8.4, h: 1.5,
    fontSize: 36, fontFace: 'Calibri', bold: true,
    color: COLORS.NEUTRAL_100,
    align: 'left',
  });

  // Subtitle / Tagline
  slide.addText(subtitle || 'The protection your customers never see you add — until it saves them', {
    x: 0.8, y: 3.1, w: 8.4, h: 0.8,
    fontSize: 18, fontFace: 'Calibri',
    color: COLORS.G300,
    align: 'left',
  });

  // Presenter and date
  slide.addText(`${presenter || 'AfriShield'}  |  ${date || new Date().toISOString().slice(0, 10)}`, {
    x: 0.8, y: 4.8, w: 8.4, h: 0.5,
    fontSize: 12, fontFace: 'Calibri',
    color: COLORS.G100,
    align: 'left',
  });

  // Accent bar
  slide.addShape(pptx.ShapeType.rect, {
    x: 0.8, y: 4.5, w: 2.0, h: 0.05,
    fill: { color: COLORS.G600 },
  });

  // Logo placeholder (bottom-right)
  slide.addText('[ AfriShield ]', {
    x: 7.8, y: 5.0, w: 1.8, h: 0.4,
    fontSize: 10, fontFace: 'Calibri', bold: true,
    color: COLORS.G600, align: 'right',
  });
  // Replace with: slide.addImage({ path: './assets/afrishield-logo.png', x: 8.2, y: 5.0, w: 1.2, h: 0.4 });
}
```

### Template 2: Section Divider (Dark)

```javascript
function addSectionSlide(pptx, { sectionTitle, sectionNumber }) {
  const slide = pptx.addSlide();
  slide.background = { color: COLORS.G800 };

  // Section number
  slide.addText(String(sectionNumber).padStart(2, '0'), {
    x: 0.8, y: 1.0, w: 2.0, h: 1.0,
    fontSize: 48, fontFace: 'Consolas',
    color: COLORS.G300, align: 'left',
  });

  // Section title
  slide.addText(sectionTitle, {
    x: 0.8, y: 2.2, w: 8.4, h: 1.2,
    fontSize: 32, fontFace: 'Calibri', bold: true,
    color: COLORS.NEUTRAL_100, align: 'left',
  });

  // Accent bar
  slide.addShape(pptx.ShapeType.rect, {
    x: 0.8, y: 3.5, w: 1.5, h: 0.05,
    fill: { color: COLORS.G600 },
  });
}
```

### Template 3: Content Slide (Light)

```javascript
function addContentSlide(pptx, { heading, bullets, footnote }) {
  const slide = pptx.addSlide();
  slide.background = { color: COLORS.NEUTRAL_100 };

  // Top accent bar
  slide.addShape(pptx.ShapeType.rect, {
    x: 0, y: 0, w: 10, h: 0.06,
    fill: { color: COLORS.G600 },
  });

  // Heading
  slide.addText(heading, {
    x: 0.8, y: 0.4, w: 8.4, h: 0.8,
    fontSize: 24, fontFace: 'Calibri', bold: true,
    color: COLORS.NEUTRAL_900, align: 'left',
  });

  // Bullet points
  const bulletRows = bullets.map(b => ({
    text: b,
    options: {
      fontSize: 16, fontFace: 'Calibri',
      color: COLORS.NEUTRAL_900,
      bullet: { code: '25CF', color: COLORS.G600 },
      paraSpaceAfter: 8,
    },
  }));

  slide.addText(bulletRows, {
    x: 0.8, y: 1.5, w: 8.4, h: 3.5,
    valign: 'top',
  });

  // Footnote
  if (footnote) {
    slide.addText(footnote, {
      x: 0.8, y: 5.0, w: 8.4, h: 0.4,
      fontSize: 10, fontFace: 'Calibri', italic: true,
      color: COLORS.G300,
    });
  }

  // Logo placeholder (bottom-right)
  slide.addText('[ AfriShield ]', {
    x: 8.2, y: 5.0, w: 1.5, h: 0.3,
    fontSize: 8, fontFace: 'Calibri', bold: true,
    color: COLORS.G100, align: 'right',
  });
}
```

### Template 4: Data Slide (Light)

```javascript
function addDataSlide(pptx, { heading, tableData, highlight }) {
  const slide = pptx.addSlide();
  slide.background = { color: COLORS.NEUTRAL_100 };

  // Top accent bar
  slide.addShape(pptx.ShapeType.rect, {
    x: 0, y: 0, w: 10, h: 0.06,
    fill: { color: COLORS.G600 },
  });

  // Heading
  slide.addText(heading, {
    x: 0.8, y: 0.4, w: 8.4, h: 0.7,
    fontSize: 22, fontFace: 'Calibri', bold: true,
    color: COLORS.NEUTRAL_900,
  });

  // Metric callout (optional)
  if (highlight) {
    slide.addText(highlight.value, {
      x: 0.8, y: 1.2, w: 3.0, h: 1.0,
      fontSize: 42, fontFace: 'Consolas', bold: true,
      color: COLORS.G600,
    });
    slide.addText(highlight.label, {
      x: 0.8, y: 2.1, w: 3.0, h: 0.5,
      fontSize: 14, fontFace: 'Calibri',
      color: COLORS.NEUTRAL_900,
    });
  }

  // Table
  // tableData is an array of arrays: first row is headers, rest is data
  const headerOpts = {
    fill: { color: COLORS.G800 },
    color: COLORS.NEUTRAL_100,
    fontSize: 12, fontFace: 'Calibri', bold: true,
    align: 'left', valign: 'middle',
  };
  const rowOpts = {
    color: COLORS.NEUTRAL_900,
    fontSize: 11, fontFace: 'Calibri',
    align: 'left', valign: 'middle',
  };
  const altRowOpts = {
    ...rowOpts,
    fill: { color: COLORS.G50 },
  };

  const formattedRows = tableData.map((row, i) =>
    row.map(cell => ({
      text: String(cell),
      options: i === 0 ? headerOpts : (i % 2 === 0 ? altRowOpts : rowOpts),
    }))
  );

  slide.addTable(formattedRows, {
    x: highlight ? 4.2 : 0.8,
    y: 1.2,
    w: highlight ? 5.5 : 8.4,
    h: 3.5,
    border: { pt: 0.5, color: COLORS.G100 },
    colW: undefined, // auto
    autoPage: false,
  });
}
```

### Template 5: Closing Slide (Dark)

```javascript
function addClosingSlide(pptx, { ctaText, contactEmail, contactUrl }) {
  const slide = pptx.addSlide();
  slide.background = { color: COLORS.G900 };

  // CTA or thank-you text
  slide.addText(ctaText || 'Ready to secure your platform?', {
    x: 0.8, y: 1.5, w: 8.4, h: 1.2,
    fontSize: 32, fontFace: 'Calibri', bold: true,
    color: COLORS.NEUTRAL_100, align: 'left',
  });

  // Contact info
  slide.addText([
    { text: contactEmail || 'hello@afrishield.com', options: { fontSize: 16, color: COLORS.G300 } },
    { text: '\n' },
    { text: contactUrl || 'afrishield.com', options: { fontSize: 16, color: COLORS.G300 } },
  ], {
    x: 0.8, y: 3.2, w: 8.4, h: 1.0,
    fontFace: 'Calibri', align: 'left',
  });

  // Accent bar
  slide.addShape(pptx.ShapeType.rect, {
    x: 0.8, y: 3.0, w: 2.0, h: 0.05,
    fill: { color: COLORS.G600 },
  });

  // Logo placeholder (bottom-right)
  slide.addText('[ AfriShield ]', {
    x: 7.8, y: 5.0, w: 1.8, h: 0.4,
    fontSize: 10, fontFace: 'Calibri', bold: true,
    color: COLORS.G600, align: 'right',
  });

  // Tagline
  slide.addText('The protection your customers never see you add — until it saves them', {
    x: 0.8, y: 4.8, w: 6.0, h: 0.4,
    fontSize: 10, fontFace: 'Calibri', italic: true,
    color: COLORS.G100,
  });
}
```

---

## Full Deck Assembly Pattern

```javascript
const PptxGenJS = require('pptxgenjs');

function generateAfriShieldDeck({ title, subtitle, presenter, date, sections, closing }) {
  const pptx = new PptxGenJS();

  // Global defaults
  pptx.layout = 'LAYOUT_WIDE';  // 13.33 x 7.5 inches -- use 'LAYOUT_16x9' for standard
  pptx.author = 'AfriShield';
  pptx.company = 'AfriShield';
  pptx.subject = title;

  // 1. Title slide (dark)
  addTitleSlide(pptx, { title, subtitle, date, presenter });

  // 2. Content sections (dark divider + light content slides)
  sections.forEach((section, idx) => {
    addSectionSlide(pptx, { sectionTitle: section.title, sectionNumber: idx + 1 });
    section.slides.forEach(slide => {
      if (slide.type === 'content') {
        addContentSlide(pptx, slide);
      } else if (slide.type === 'data') {
        addDataSlide(pptx, slide);
      }
    });
  });

  // 3. Closing slide (dark)
  addClosingSlide(pptx, closing || {});

  return pptx;
}
```

---

## Execution Instructions

When the user asks for a branded deck, follow this procedure:

1. **Gather content.** Confirm the deck purpose, audience, and key data points. Determine which slide templates are needed.

2. **Assemble the script.** Build a complete Node.js script that:
   - Requires `pptxgenjs`
   - Defines all color constants and template functions from this skill
   - Calls `generateAfriShieldDeck()` with the user's content
   - Writes the output with `pptx.writeFile({ fileName: 'afrishield-[topic]-[audience]-[YYYY-MM-DD].pptx' })`

3. **Run in workspace bash.** Execute:
   ```bash
   cd /tmp && npm init -y && npm install pptxgenjs
   node generate-deck.js
   ```

4. **Deliver the file.** Copy the generated .pptx to the outputs folder and present it to the user.

---

## Slide Sequence Rules

| Position | Slide type | Background |
|---|---|---|
| First | Title | Dark (G900) |
| Before each section | Section divider | Dark (G800) |
| Section content | Content or Data | Light (Neutral-100) |
| Last | Closing / CTA | Dark (G900) |

This creates the **sandwich pattern**: dark-light-dark-light-...-dark.

---

## Layout Constants

```javascript
const LAYOUT = {
  MARGIN_LEFT:   0.8,   // inches
  MARGIN_RIGHT:  0.8,
  MARGIN_TOP:    0.4,
  CONTENT_WIDTH: 8.4,   // 10 - left - right margins
  ACCENT_BAR_H:  0.05,  // thin accent line height
  LOGO_X:        8.2,
  LOGO_Y:        5.0,
  LOGO_W:        1.2,
  LOGO_H:        0.4,
};
```

---

## Common Deck Types

### Sales Deck
Title -> Company Overview -> Problem Statement -> Solution -> Case Study (data slide) -> Pricing -> Closing/CTA

### Board Update
Title -> Executive Summary -> Revenue by Line (data) -> Pipeline (data) -> Key Wins -> Risks -> Next Quarter -> Closing

### Technical Proposal
Title -> Challenge -> Architecture Overview -> Implementation Plan -> Timeline (data) -> Team -> Investment -> Closing

### Marketing Report
Title -> Campaign Summary -> Channel Performance (data) -> Lead Generation (data) -> Content Metrics -> Recommendations -> Closing
