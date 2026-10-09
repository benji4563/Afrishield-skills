/**
 * Forward a form payload to a Make.com webhook. The webhook URL stays on the
 * server, so it is never exposed in the browser bundle.
 */
export async function forwardToWebhook(url: string | undefined, payload: Record<string, unknown>): Promise<boolean> {
  if (!url) {
    console.warn(`[local-seo] webhook URL not set; dropped payload of type "${String(payload.type)}"`);
    return false;
  }
  const apiKey = process.env.MAKE_WEBHOOK_API_KEY;
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...(apiKey ? { 'x-make-apikey': apiKey } : {}) },
    body: JSON.stringify(payload),
  });
  return response.ok;
}

export function clean(value: unknown, max: number): string {
  return typeof value === 'string' ? value.trim().slice(0, max) : '';
}
