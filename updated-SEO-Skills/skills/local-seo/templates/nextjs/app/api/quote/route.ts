import { NextResponse } from 'next/server';
import { getBusiness } from '@/lib/local-seo/business';
import { clean, forwardToWebhook } from '@/lib/local-seo/webhook';

/** Quote requests from Service x City pages. Forwards to QUOTE_WEBHOOK_URL. */
export async function POST(request: Request) {
  const body = (await request.json().catch(() => null)) as Record<string, unknown> | null;
  if (!body) return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 });
  if (clean(body.company, 200)) return NextResponse.json({ ok: true }); // honeypot

  const name = clean(body.name, 120);
  const phone = clean(body.phone, 40);
  if (!name || !phone) return NextResponse.json({ error: 'Name and phone are required' }, { status: 400 });

  const delivered = await forwardToWebhook(process.env.QUOTE_WEBHOOK_URL, {
    type: 'quote_request',
    business: getBusiness().name,
    name,
    phone,
    details: clean(body.details, 4000),
    service: clean(body.service, 120),
    city: clean(body.city, 120),
    page_url: clean(body.page_url, 500),
    submitted_at: new Date().toISOString(),
  });
  return delivered
    ? NextResponse.json({ ok: true })
    : NextResponse.json({ error: 'Could not deliver the request' }, { status: 502 });
}
