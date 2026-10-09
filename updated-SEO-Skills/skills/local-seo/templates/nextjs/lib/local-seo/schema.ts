import type { Business, ServiceCityPage } from './types';
import { serviceCityPath } from './pages';

const businessId = (site: string) => `${site}/#business`;

/** LocalBusiness with exact coordinates. NAP comes only from business.json, so it cannot drift. */
export function localBusinessJsonLd(business: Business, site: string, page?: ServiceCityPage): object {
  const { address, geo } = business;
  return {
    '@context': 'https://schema.org',
    '@type': business.schema_type ?? 'LocalBusiness',
    '@id': businessId(site),
    name: business.name,
    description: business.description,
    url: site,
    telephone: business.phone,
    ...(business.email ? { email: business.email } : {}),
    ...(business.price_range ? { priceRange: business.price_range } : {}),
    ...(business.opening_hours?.length ? { openingHours: business.opening_hours } : {}),
    address: {
      '@type': 'PostalAddress',
      // A service-area business that hides its address publishes locality only.
      ...(!business.hide_address && address.street ? { streetAddress: address.street } : {}),
      addressLocality: address.locality,
      addressRegion: address.region,
      ...(!business.hide_address && address.postal_code ? { postalCode: address.postal_code } : {}),
      addressCountry: address.country,
    },
    ...(geo.lat !== null && geo.lng !== null
      ? { geo: { '@type': 'GeoCoordinates', latitude: geo.lat, longitude: geo.lng } }
      : {}),
    areaServed: page
      ? serviceArea(page)
      : business.service_areas.map((area) => ({ '@type': 'City', name: area.split(',')[0].trim() })),
    ...(business.same_as?.length || business.gbp?.profile_url
      ? { sameAs: [business.gbp?.profile_url, ...(business.same_as ?? [])].filter(Boolean) }
      : {}),
  };
}

/** The named city plus a GeoCircle boundary around the page's own coordinates. */
function serviceArea(page: ServiceCityPage): object[] {
  return [
    {
      '@type': 'City',
      name: page.cityName,
      containedInPlace: { '@type': 'AdministrativeArea', name: page.region },
    },
    {
      '@type': 'GeoCircle',
      geoMidpoint: { '@type': 'GeoCoordinates', latitude: page.geo.lat, longitude: page.geo.lng },
      geoRadius: page.serviceRadiusKm * 1000,
    },
  ];
}

export function serviceJsonLd(business: Business, site: string, page: ServiceCityPage): object {
  return {
    '@context': 'https://schema.org',
    '@type': 'Service',
    '@id': `${site}${serviceCityPath(page)}#service`,
    name: `${page.serviceName} in ${page.cityName}`,
    serviceType: page.serviceName,
    description: page.definition,
    url: `${site}${serviceCityPath(page)}`,
    provider: { '@id': businessId(site), '@type': business.schema_type ?? 'LocalBusiness', name: business.name },
    areaServed: serviceArea(page),
  };
}

/** Only ever built from the same array the visible FAQ renders, so markup and page cannot disagree. */
export function faqPageJsonLd(items: Array<{ q: string; a: string }>): object {
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: items.map(({ q, a }) => ({
      '@type': 'Question',
      name: q,
      acceptedAnswer: { '@type': 'Answer', text: a },
    })),
  };
}

export function breadcrumbJsonLd(site: string, trail: Array<{ name: string; path: string }>): object {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: trail.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.name,
      item: `${site}${item.path}`,
    })),
  };
}
