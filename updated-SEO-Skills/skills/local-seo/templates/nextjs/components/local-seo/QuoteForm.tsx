'use client';

import { useState, type FormEvent } from 'react';

type Props = {
  service: string;
  city: string;
  phone: string;
  phoneHref: string;
};

/** Above-the-fold instant quote form with a click-to-call fallback. Posts to /api/quote. */
export function QuoteForm({ service, city, phone, phoneHref }: Props) {
  const [state, setState] = useState<'idle' | 'sending' | 'sent' | 'error'>('idle');

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setState('sending');
    try {
      const response = await fetch('/api/quote', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...Object.fromEntries(form), service, city, page_url: window.location.href }),
      });
      setState(response.ok ? 'sent' : 'error');
    } catch {
      setState('error');
    }
  }

  if (state === 'sent') {
    return (
      <div role="status" className="rounded-lg bg-white p-6 shadow-lg ring-1 ring-slate-200">
        <p className="text-lg font-semibold text-slate-900">Thanks — your request is in.</p>
        <p className="mt-2 text-slate-700">
          We will reply shortly. Need someone now? Call{' '}
          <a href={phoneHref} className="font-semibold underline">
            {phone}
          </a>
          .
        </p>
      </div>
    );
  }

  const field = 'mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-slate-900';
  return (
    <form onSubmit={submit} className="rounded-lg bg-white p-6 shadow-lg ring-1 ring-slate-200">
      <p className="text-lg font-semibold text-slate-900">
        Get a {service.toLowerCase()} quote in {city}
      </p>
      <label className="mt-4 block text-sm font-medium text-slate-700">
        Name
        <input name="name" required autoComplete="name" className={field} />
      </label>
      <label className="mt-3 block text-sm font-medium text-slate-700">
        Phone
        <input name="phone" type="tel" required autoComplete="tel" className={field} />
      </label>
      <label className="mt-3 block text-sm font-medium text-slate-700">
        What do you need?
        <textarea name="details" rows={3} className={field} />
      </label>
      {/* Honeypot: hidden from people, filled by bots. */}
      <input name="company" tabIndex={-1} autoComplete="off" aria-hidden="true" className="hidden" />
      <button
        type="submit"
        disabled={state === 'sending'}
        className="mt-5 w-full rounded-md bg-slate-900 px-4 py-3 font-semibold text-white disabled:opacity-60"
      >
        {state === 'sending' ? 'Sending…' : 'Get my quote'}
      </button>
      {state === 'error' && (
        <p role="alert" className="mt-3 text-sm text-red-700">
          That did not send. Please call{' '}
          <a href={phoneHref} className="underline">
            {phone}
          </a>
          .
        </p>
      )}
      <p className="mt-3 text-center text-sm text-slate-600">
        or call{' '}
        <a href={phoneHref} className="font-semibold underline">
          {phone}
        </a>
      </p>
    </form>
  );
}
