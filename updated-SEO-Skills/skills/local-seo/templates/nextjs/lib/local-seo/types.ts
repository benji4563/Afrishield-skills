export type Business = {
  name: string;
  legal_name?: string;
  description: string;
  schema_type?: string;
  website: string;
  phone: string;
  email?: string;
  address: {
    street?: string;
    locality: string;
    region: string;
    postal_code?: string;
    country: string;
  };
  service_area_business?: boolean;
  hide_address?: boolean;
  geo: { lat: number | null; lng: number | null };
  primary_metro: string;
  price_range?: string;
  opening_hours?: string[];
  services: Array<{ slug: string; name: string; keywords?: string[]; description?: string }>;
  service_areas: string[];
  gbp?: { profile_url?: string; review_link?: string };
  same_as?: string[];
};

export type Testimonial = {
  quote: string;
  author: string;
  neighborhood?: string;
  date?: string;
  source?: 'google' | 'direct';
  /** true only when the client supplied this exact quote. Unverified quotes never render. */
  verified: boolean;
};

export type ServiceCityPage = {
  status: 'draft' | 'ready';
  service: string;
  serviceName: string;
  city: string;
  cityName: string;
  region: string;
  primaryKeyword: string;
  secondaryKeywords: string[];
  title: string;
  metaDescription: string;
  h1: string;
  /** 40-70 words, plain facts. The block AI engines lift as a citation. */
  definition: string;
  intro: string;
  local: {
    landmarks: Array<{ name: string; context: string }>;
    crossStreets: string[];
    neighborhoods: string[];
    localNotes: string;
  };
  testimonials: Testimonial[];
  projects: Array<{ title: string; neighborhood: string; summary: string; date?: string }>;
  /** summary: one sentence stating the table's takeaway, shown above it. */
  comparison: { caption: string; summary: string; columns: string[]; rows: string[][] };
  faqs: Array<{ q: string; a: string }>;
  geo: { lat: number; lng: number };
  serviceRadiusKm: number;
  updated?: string;
};
