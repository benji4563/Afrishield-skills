import { NextResponse } from 'next/server';
import { getBusiness } from '@/lib/local-seo/business';
import { clean, forwardToWebhook } from '@/lib/local-seo/webhook';

/**
 * Private feedback from a 1-3 star rating. Forwards to the Make.com webhook
 * (MAKE_REVIEW_WEBHOOK_URL) whose scenario posts it to the private Slack channel.
 */
export async function POST(request: Request) {
  const body = (await request.json().catch(() => null)) as Record<string, unknown> | null;
  if (!body) return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 });
  if (clean(body.company, 200)) return NextResponse.json({ ok: true }); // honeypot: pretend it worked

  const rating = Number(body.rating);
  const feedback = clean(body.feedback, 4000);
  if (!Number.isInteger(rating) || rating < 1 || rating > 3 || !feedback) {
    return NextResponse.json({ error: 'A 1-3 star rating and feedback are required' }, { status: 400 });
  }

  const delivered = await forwardToWebhook(process.env.MAKE_REVIEW_WEBHOOK_URL, {
    type: 'review_feedback',
    business: getBusiness().name,
    rating,
    feedback,
    name: clean(body.name, 120),
    contact: clean(body.contact, 200),
    context: clean(body.context, 80),
    page_url: clean(body.page_url, 500),
    submitted_at: new Date().toISOString(),
  });
  return delivered
    ? NextResponse.json({ ok: true })
    : NextResponse.json({ error: 'Could not deliver feedback' }, { status: 502 });
}
