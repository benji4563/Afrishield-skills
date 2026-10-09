import fs from 'node:fs';
import path from 'node:path';
import type { Business } from './types';

let cached: Business | undefined;

/** The single source of truth for NAP. Read at build time from local-seo/business.json. */
export function getBusiness(): Business {
  if (!cached) {
    const file = path.join(process.cwd(), 'local-seo', 'business.json');
    cached = JSON.parse(fs.readFileSync(file, 'utf8')) as Business;
  }
  return cached;
}

export function siteUrl(): string {
  return (process.env.NEXT_PUBLIC_SITE_URL ?? getBusiness().website).replace(/\/$/, '');
}

/** "+1-416-555-0100" -> "tel:+14165550100" */
export function telHref(phone: string): string {
  return `tel:${phone.replace(/[^\d+]/g, '')}`;
}
