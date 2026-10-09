import fs from 'node:fs';
import path from 'node:path';
import type { ServiceCityPage } from './types';

const PAGES_DIR = path.join(process.cwd(), 'content', 'local-seo', 'pages');

let cached: ServiceCityPage[] | undefined;

/**
 * Service x City pages. Only pages marked "ready" are built in production:
 * a page reaches "ready" after scripts/doorway_check.py passes it. Drafts are
 * visible in development for preview. Files starting with "_" are examples.
 */
export function getServiceCityPages(): ServiceCityPage[] {
  if (!cached) {
    const includeDrafts = process.env.NODE_ENV !== 'production';
    const files = fs.existsSync(PAGES_DIR)
      ? fs.readdirSync(PAGES_DIR).filter((f) => f.endsWith('.json') && !f.startsWith('_'))
      : [];
    cached = files
      .map((f) => JSON.parse(fs.readFileSync(path.join(PAGES_DIR, f), 'utf8')) as ServiceCityPage)
      .filter((p) => p.status === 'ready' || includeDrafts);
  }
  return cached;
}

export function getServiceCityPage(service: string, city: string): ServiceCityPage | undefined {
  return getServiceCityPages().find((p) => p.service === service && p.city === city);
}

export function serviceCityPath(page: Pick<ServiceCityPage, 'service' | 'city'>): string {
  return `/services/${page.service}/${page.city}`;
}

/** Other cities for the same service, and other services in the same city. */
export function relatedPages(page: ServiceCityPage): ServiceCityPage[] {
  return getServiceCityPages()
    .filter((p) => p !== page && (p.service === page.service || p.city === page.city))
    .slice(0, 6);
}

/** Spread into the site's sitemap route. */
export function serviceCitySitemapEntries(): Array<{ path: string; priority: string; changefreq: string; lastmod?: string }> {
  return getServiceCityPages()
    .filter((p) => p.status === 'ready')
    .map((p) => ({ path: serviceCityPath(p), priority: '0.8', changefreq: 'monthly', lastmod: p.updated }));
}
