import type { Metadata } from 'next';
import { ReviewGate } from '@/components/local-seo/ReviewGate';
import { getBusiness } from '@/lib/local-seo/business';

// Sent to customers by link or QR code; it has no place in search results.
export const metadata: Metadata = {
  title: 'Rate your experience',
  robots: { index: false, follow: false },
};

export default async function ReviewPage({
  searchParams,
}: {
  searchParams: Promise<{ ref?: string | string[] }>;
}) {
  const { ref } = await searchParams;
  const business = getBusiness();
  const reviewLink = business.gbp?.review_link;
  if (!reviewLink || reviewLink.includes('TODO')) {
    throw new Error('Set gbp.review_link in local-seo/business.json (https://g.page/r/<id>/review).');
  }
  return (
    <main className="flex min-h-screen items-center bg-slate-50 px-6 py-12">
      <ReviewGate
        businessName={business.name}
        googleReviewUrl={reviewLink}
        context={typeof ref === 'string' ? ref.slice(0, 80) : ''}
      />
    </main>
  );
}
