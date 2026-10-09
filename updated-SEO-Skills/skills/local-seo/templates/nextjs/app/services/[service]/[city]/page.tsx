import type { Metadata } from 'next';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { JsonLd } from '@/components/local-seo/JsonLd';
import { QuoteForm } from '@/components/local-seo/QuoteForm';
import { ComparisonTable, DefinitionBlock, FaqSection, LocalProof, LocalWork } from '@/components/local-seo/sections';
import { getBusiness, siteUrl, telHref } from '@/lib/local-seo/business';
import { getServiceCityPage, getServiceCityPages, relatedPages, serviceCityPath } from '@/lib/local-seo/pages';
import { breadcrumbJsonLd, faqPageJsonLd, localBusinessJsonLd, serviceJsonLd } from '@/lib/local-seo/schema';

type Params = { service: string; city: string };

// Only the pages in content/local-seo/pages exist. No page is invented from a URL.
export const dynamicParams = false;

export function generateStaticParams(): Params[] {
  return getServiceCityPages().map(({ service, city }) => ({ service, city }));
}

export async function generateMetadata({ params }: { params: Promise<Params> }): Promise<Metadata> {
  const { service, city } = await params;
  const page = getServiceCityPage(service, city);
  if (!page) return {};
  const url = `${siteUrl()}${serviceCityPath(page)}`;
  return {
    title: page.title,
    description: page.metaDescription,
    alternates: { canonical: url },
    // Drafts are previewable in development but must never be indexed.
    robots: page.status === 'ready' ? undefined : { index: false, follow: false },
    openGraph: { title: page.title, description: page.metaDescription, url, type: 'website' },
    twitter: { card: 'summary_large_image', title: page.title, description: page.metaDescription },
  };
}

export default async function ServiceCityPage({ params }: { params: Promise<Params> }) {
  const { service, city } = await params;
  const page = getServiceCityPage(service, city);
  if (!page) notFound();

  const business = getBusiness();
  const site = siteUrl();
  const phoneHref = telHref(business.phone);
  const related = relatedPages(page);

  return (
    <>
      <JsonLd data={localBusinessJsonLd(business, site, page)} />
      <JsonLd data={serviceJsonLd(business, site, page)} />
      <JsonLd data={faqPageJsonLd(page.faqs)} />
      <JsonLd
        data={breadcrumbJsonLd(site, [
          { name: 'Home', path: '/' },
          { name: 'Services', path: '/services' },
          { name: `${page.serviceName} in ${page.cityName}`, path: serviceCityPath(page) },
        ])}
      />

      <main className="mx-auto w-full max-w-6xl px-6 md:px-10">
        <section className="grid gap-10 py-12 md:grid-cols-[3fr_2fr] md:py-16">
          <div>
            <h1 className="text-4xl font-bold tracking-tight text-slate-900 md:text-5xl">{page.h1}</h1>
            <DefinitionBlock text={page.definition} />
            <p className="mt-6 max-w-prose text-slate-700">{page.intro}</p>
            <a
              href={phoneHref}
              className="mt-6 inline-block rounded-md border-2 border-slate-900 px-5 py-3 font-semibold text-slate-900"
            >
              Call {business.phone}
            </a>
          </div>
          <QuoteForm service={page.serviceName} city={page.cityName} phone={business.phone} phoneHref={phoneHref} />
        </section>

        <LocalProof page={page} />
        <LocalWork page={page} />

        <section aria-labelledby="compare-heading" className="py-12">
          <h2 id="compare-heading" className="text-2xl font-semibold text-slate-900">
            {page.serviceName} options in {page.cityName}, compared
          </h2>
          <ComparisonTable comparison={page.comparison} />
        </section>

        <FaqSection heading={`${page.serviceName} in ${page.cityName}: common questions`} items={page.faqs} />

        {/* Visible NAP, identical to the JSON-LD above because both read business.json. */}
        <address className="border-t border-slate-200 py-8 not-italic text-slate-700">
          <strong className="text-slate-900">{business.name}</strong>
          <br />
          {!business.hide_address && business.address.street ? `${business.address.street}, ` : ''}
          {business.address.locality}, {business.address.region}
          {!business.hide_address && business.address.postal_code ? ` ${business.address.postal_code}` : ''}
          <br />
          <a href={phoneHref} className="underline">
            {business.phone}
          </a>
        </address>

        {related.length > 0 && (
          <nav aria-labelledby="related-heading" className="py-12">
            <h2 id="related-heading" className="text-2xl font-semibold text-slate-900">
              Nearby areas and related services
            </h2>
            <ul className="mt-4 grid gap-2 md:grid-cols-3">
              {related.map((other) => (
                <li key={serviceCityPath(other)}>
                  <Link href={serviceCityPath(other)} className="text-slate-900 underline">
                    {other.serviceName} in {other.cityName}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        )}
      </main>
    </>
  );
}
