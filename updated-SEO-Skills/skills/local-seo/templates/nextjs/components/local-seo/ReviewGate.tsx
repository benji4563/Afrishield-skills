'use client';

import { useEffect, useState, type FormEvent } from 'react';

type Props = {
  businessName: string;
  /** The profile's review link, https://g.page/r/<id>/review */
  googleReviewUrl: string;
  /** Free-text context carried into the Slack alert, e.g. "drain-cleaning / etobicoke". */
  context?: string;
  /**
   * Keep the Google link visible to low raters too. Google's review policy
   * forbids selectively soliciting positive reviews, and hiding the link from
   * unhappy customers is exactly that. Turn this off only on legal advice.
   */
  publicLinkForAll?: boolean;
  redirectDelayMs?: number;
};

const LABELS = ['Poor', 'Fair', 'OK', 'Good', 'Excellent'];

/**
 * Review intake. 4-5 stars: redirect to the Google review form. 1-3 stars:
 * collect private feedback and POST it to /api/review-feedback, which forwards
 * it to the Make.com webhook that alerts the team in Slack.
 */
export function ReviewGate({
  businessName,
  googleReviewUrl,
  context = '',
  publicLinkForAll = true,
  redirectDelayMs = 1500,
}: Props) {
  const [rating, setRating] = useState(0);
  const [hover, setHover] = useState(0);
  const [state, setState] = useState<'idle' | 'sending' | 'sent' | 'error'>('idle');
  const happy = rating >= 4;

  useEffect(() => {
    if (!happy) return;
    const timer = window.setTimeout(() => window.location.assign(googleReviewUrl), redirectDelayMs);
    return () => window.clearTimeout(timer);
  }, [happy, googleReviewUrl, redirectDelayMs]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setState('sending');
    try {
      const response = await fetch('/api/review-feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...Object.fromEntries(form), rating, context, page_url: window.location.href }),
      });
      setState(response.ok ? 'sent' : 'error');
    } catch {
      setState('error');
    }
  }

  const publicLink = publicLinkForAll && (
    <p className="mt-6 text-sm text-slate-600">
      Prefer to post publicly?{' '}
      <a href={googleReviewUrl} className="underline">
        Leave a Google review
      </a>
      .
    </p>
  );

  return (
    <div className="mx-auto max-w-md rounded-lg bg-white p-8 text-center shadow-lg ring-1 ring-slate-200">
      <h1 className="text-2xl font-semibold text-slate-900">How did we do?</h1>
      <p className="mt-2 text-slate-600">Rate your experience with {businessName}.</p>

      <div role="radiogroup" aria-label="Star rating" className="mt-6 flex justify-center gap-1">
        {LABELS.map((label, index) => {
          const value = index + 1;
          const lit = value <= (hover || rating);
          return (
            <button
              key={label}
              type="button"
              role="radio"
              aria-checked={rating === value}
              aria-label={`${value} star${value > 1 ? 's' : ''} — ${label}`}
              disabled={state === 'sent'}
              onClick={() => setRating(value)}
              onMouseEnter={() => setHover(value)}
              onMouseLeave={() => setHover(0)}
              className={`text-4xl leading-none transition-colors ${lit ? 'text-amber-400' : 'text-slate-300'}`}
            >
              ★
            </button>
          );
        })}
      </div>

      {happy && (
        <div role="status" className="mt-6">
          <p className="font-semibold text-slate-900">Thank you! Taking you to Google to share that…</p>
          <a href={googleReviewUrl} className="mt-3 inline-block rounded-md bg-slate-900 px-5 py-3 font-semibold text-white">
            Continue to Google
          </a>
        </div>
      )}

      {rating > 0 && !happy && state !== 'sent' && (
        <form onSubmit={submit} className="mt-6 text-left">
          <p className="text-slate-800">We are sorry we fell short. Tell us what happened and a manager will follow up.</p>
          <label className="mt-4 block text-sm font-medium text-slate-700">
            What went wrong?
            <textarea name="feedback" required rows={4} className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2" />
          </label>
          <label className="mt-3 block text-sm font-medium text-slate-700">
            Your name
            <input name="name" autoComplete="name" className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2" />
          </label>
          <label className="mt-3 block text-sm font-medium text-slate-700">
            Phone or email, so we can put it right
            <input name="contact" className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2" />
          </label>
          <input name="company" tabIndex={-1} autoComplete="off" aria-hidden="true" className="hidden" />
          <button
            type="submit"
            disabled={state === 'sending'}
            className="mt-5 w-full rounded-md bg-slate-900 px-4 py-3 font-semibold text-white disabled:opacity-60"
          >
            {state === 'sending' ? 'Sending…' : 'Send to the manager'}
          </button>
          {state === 'error' && (
            <p role="alert" className="mt-3 text-sm text-red-700">
              That did not send. Please try again.
            </p>
          )}
          {publicLink}
        </form>
      )}

      {state === 'sent' && (
        <div role="status" className="mt-6">
          <p className="font-semibold text-slate-900">Thank you. Your feedback went straight to our manager.</p>
          {publicLink}
        </div>
      )}
    </div>
  );
}
