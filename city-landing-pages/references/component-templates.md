# Component Templates

These are the reference implementations from the njaccountstax.com build. Adapt to the project's design system — colors, fonts, spacing, component names.

Read this file when scaffolding city components on a fresh project. On an existing project that already has these components, skip this file.

## CityHero.tsx

```tsx
import { Button } from '@/components/design-system/Button';
import { Emphasis } from '@/components/signature/UnderlineSwoosh';
import { BlobImage } from '@/components/signature/BlobImage';
import { ResponseTimeBadge } from '@/components/proof/ResponseTimeBadge';

type Props = {
  cityName: string;
  description: string;
  floatingHeadline: string;
  floatingSubline: string;
};

export function CityHero({ cityName, description, floatingHeadline, floatingSubline }: Props) {
  return (
    <section className="relative overflow-hidden bg-cream">
      <div className="container-content grid gap-12 py-20 md:grid-cols-[1.15fr_1fr] md:py-24 lg:gap-16">
        <div className="max-w-[560px]">
          <ResponseTimeBadge />

          <h1 className="mt-6 font-display text-display-mobile leading-[1.05] tracking-[-0.02em] text-aubergine md:text-display">
            A small-business{' '}
            <Emphasis>accountant</Emphasis>
            <br />
            in <Emphasis>{cityName}</Emphasis>.
          </h1>

          <p className="mt-8 max-w-[480px] text-body-lg text-graphite">
            {description}
          </p>

          <div className="mt-8 flex flex-wrap items-center gap-6">
            <Button href="/contact" variant="primary" showArrow>
              Book a free 15-min call
            </Button>
            <Button href="/pricing" variant="tertiary">
              See our pricing
            </Button>
          </div>
        </div>

        <div className="relative">
          <BlobImage src="/njock-portrait.webp" alt="Njock Simon Ndum, Co-founder and CEO" />

          <div className="absolute bottom-10 left-0 z-20 flex max-w-[260px] items-center gap-3 rounded-card bg-ivory px-5 py-4 shadow-elevated">
            <div
              className="h-2.5 w-2.5 shrink-0 rounded-full bg-sage"
              style={{ boxShadow: '0 0 0 4px rgba(117,143,115,.2)' }}
            />
            <div className="text-body-sm">
              <div className="font-display text-[15px] font-medium text-aubergine">
                {floatingHeadline}
              </div>
              <div className="text-graphite/70">{floatingSubline}</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
```

**Adaptation notes:**
- Replace `bg-cream`, `text-aubergine`, `text-graphite`, `bg-sage`, etc. with the project's color tokens
- Replace `font-display`, `text-display-mobile`, `text-body-lg` with the project's type scale
- Replace `BlobImage`, `ResponseTimeBadge`, `Button`, `Emphasis` with whatever the project uses — or create simpler versions (a regular `<img>`, a styled `<a>`, a `<span>` with underline)
- The floating badge is optional but adds credibility

## CityLocalTrust.tsx

```tsx
import { Section } from '@/components/design-system/Section';

type Props = {
  heading: string;
  paragraphs: string[];
  neighborhoods: string[];
};

export function CityLocalTrust({ heading, paragraphs, neighborhoods }: Props) {
  return (
    <Section background="ivory">
      <div className="grid gap-10 md:grid-cols-[1.4fr_1fr] md:gap-16">
        <div>
          <div className="section-eyebrow mb-3">Where we work</div>
          <h2 className="font-display text-h2 text-aubergine">{heading}</h2>
          {paragraphs.map((p, i) => (
            <p key={i} className="mt-6 text-body text-graphite first:mt-6">
              {p}
            </p>
          ))}
        </div>

        <div>
          <div className="section-eyebrow mb-3">Neighborhoods we serve</div>
          <ul className="grid grid-cols-2 gap-x-4 gap-y-2 text-body-sm text-aubergine">
            {neighborhoods.map((n) => (
              <li key={n} className="flex items-center gap-2">
                <span
                  aria-hidden
                  className="h-1.5 w-1.5 shrink-0 rounded-full bg-persimmon"
                />
                {n}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </Section>
  );
}
```

**Adaptation notes:**
- The two-column layout (content left, neighborhood list right) works well on desktop. On mobile it stacks.
- `section-eyebrow` is a small uppercase label — replace with whatever the project uses for section labels
- The bullet dot uses the brand accent color

## CityFaq.tsx

```tsx
import { Section } from '@/components/design-system/Section';

type Props = {
  eyebrow: string;
  heading: string;
  items: Array<{ q: string; a: string }>;
};

export function CityFaq({ eyebrow, heading, items }: Props) {
  return (
    <Section background="cream">
      <div className="container-prose">
        <div className="section-eyebrow mb-3">{eyebrow}</div>
        <h2 className="font-display text-h2 text-aubergine">{heading}</h2>
        <dl className="mt-10 divide-y divide-aubergine/10">
          {items.map((item) => (
            <div key={item.q} className="py-6">
              <dt className="font-display text-h4 text-aubergine">{item.q}</dt>
              <dd className="mt-3 text-body text-graphite">{item.a}</dd>
            </div>
          ))}
        </dl>
      </div>
    </Section>
  );
}
```

**Adaptation notes:**
- Uses a `<dl>` (definition list) for semantic correctness — screen readers announce question/answer pairs
- The divider between items uses a very light border
- `container-prose` constrains width for readability — typically ~65ch or 720px max

## CityConfig type (city-data.ts)

```typescript
export type CityConfig = {
  slug: string;
  name: string;
  state: string;
  stateCode: string;
  county: string;
  metaTitle: string;
  metaDescription: string;
  heroDescription: string;
  floatingBadge: { headline: string; subline: string };
  neighborhoods: string[];
  localTrustHeading: string;
  localTrustBody: string[];
  localTrustRadius: string;
  faqEyebrow: string;
  faqHeading: string;
  faqs: Array<{ q: string; a: string }>;
};
```

## Page file template

```tsx
import type { Metadata } from 'next';
import { CityHero } from '@/components/locations/CityHero';
import { CityLocalTrust } from '@/components/locations/CityLocalTrust';
import { CityFaq } from '@/components/locations/CityFaq';
// Import shared home page components as available:
// import { ProofStrip } from '@/components/home/ProofStrip';
// import { ServicesGrid } from '@/components/home/ServicesGrid';
// etc.
import { StructuredData } from '@/components/seo/StructuredData';
import {
  localBusinessJsonLd,
  faqPageJsonLd,
  breadcrumbJsonLd,
} from '@/lib/structured-data';
import { CITY_NAME } from '@/lib/city-data';

const c = CITY_NAME;

export const metadata: Metadata = {
  title: c.metaTitle,
  description: c.metaDescription,
  alternates: { canonical: `/locations/${c.slug}` },
  openGraph: {
    title: c.metaTitle,
    description: c.metaDescription,
    url: `https://DOMAIN/locations/${c.slug}`,
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: c.metaTitle,
    description: c.metaDescription,
  },
};

export default function CityLandingPage() {
  return (
    <>
      <StructuredData
        data={localBusinessJsonLd({
          name: c.name,
          region: c.state,
          regionCode: c.stateCode,
        })}
      />
      <StructuredData data={faqPageJsonLd(c.faqs)} />
      <StructuredData
        data={breadcrumbJsonLd([
          { name: 'Home', path: '/' },
          { name: 'Locations', path: `/locations/${c.slug}` },
          { name: c.name, path: `/locations/${c.slug}` },
        ])}
      />

      <CityHero
        cityName={c.name}
        description={c.heroDescription}
        floatingHeadline={c.floatingBadge.headline}
        floatingSubline={c.floatingBadge.subline}
      />
      {/* <ProofStrip /> */}
      <CityLocalTrust
        heading={c.localTrustHeading}
        paragraphs={c.localTrustBody}
        neighborhoods={c.neighborhoods}
      />
      {/* <EmotionalRecognition /> */}
      {/* <ServicesGrid /> */}
      {/* <MeetNjock /> */}
      {/* <FirstThirtyDays /> */}
      <CityFaq eyebrow={c.faqEyebrow} heading={c.faqHeading} items={c.faqs} />
      {/* <PricingPreview /> */}
      {/* <CtaDrop /> */}
    </>
  );
}
```

Uncomment shared components as they exist in the project. The three city-specific sections (Hero, LocalTrust, FAQ) are the minimum viable page.

## JSON-LD helper functions

If the project doesn't have structured data helpers yet, create `lib/structured-data.ts`:

```typescript
const SITE_URL = 'https://yourdomain.com';
const BUSINESS_NAME = 'Your Business Name';
const BUSINESS_EMAIL = 'hello@yourdomain.com';

export function localBusinessJsonLd(city: {
  name: string;
  region: string;
  regionCode: string;
  country?: string;
}) {
  return {
    '@context': 'https://schema.org',
    '@type': 'LocalBusiness',
    '@id': `${SITE_URL}/locations/${city.name.toLowerCase().replace(/\s+/g, '-')}#localbusiness`,
    name: `${BUSINESS_NAME} — ${city.name}`,
    url: `${SITE_URL}/locations/${city.name.toLowerCase().replace(/\s+/g, '-')}`,
    email: BUSINESS_EMAIL,
    priceRange: '$$',
    description: `Services serving ${city.name}, ${city.region} — remote delivery, flat monthly pricing.`,
    areaServed: {
      '@type': 'City',
      name: city.name,
      containedInPlace: { '@type': 'AdministrativeArea', name: city.region },
    },
    address: {
      '@type': 'PostalAddress',
      addressLocality: city.name,
      addressRegion: city.regionCode,
      addressCountry: city.country ?? 'US',
    },
  };
}

export function faqPageJsonLd(items: Array<{ q: string; a: string }>) {
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: items.map((it) => ({
      '@type': 'Question',
      name: it.q,
      acceptedAnswer: { '@type': 'Answer', text: it.a },
    })),
  };
}

export function breadcrumbJsonLd(trail: Array<{ name: string; path: string }>) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: trail.map((t, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      name: t.name,
      item: `${SITE_URL}${t.path}`,
    })),
  };
}
```
