import type { ServiceCityPage } from '@/lib/local-seo/types';

/**
 * The citable block: 40-70 words of plain fact directly under the H1. Keep it
 * as one <p> so answer engines can lift it whole.
 */
export function DefinitionBlock({ text }: { text: string }) {
  return (
    <p className="mt-6 border-l-4 border-slate-900 bg-slate-50 p-5 text-lg leading-relaxed text-slate-800">
      {text}
    </p>
  );
}

/** Landmarks, cross streets and neighbourhoods: the content a city-name swap cannot fake. */
export function LocalProof({ page }: { page: ServiceCityPage }) {
  const { landmarks, crossStreets, neighborhoods, localNotes } = page.local;
  return (
    <section aria-labelledby="local-heading" className="py-12">
      <h2 id="local-heading" className="text-2xl font-semibold text-slate-900">
        Where we work in {page.cityName}
      </h2>
      <p className="mt-4 max-w-prose text-slate-700">
        We provide {page.serviceName.toLowerCase()} throughout {page.cityName}, {page.region}, including{' '}
        {neighborhoods.slice(0, 4).join(', ')} and the streets around {crossStreets[0]}.
      </p>
      {localNotes.split(/\n{2,}/).map((paragraph) => (
        <p key={paragraph.slice(0, 40)} className="mt-4 max-w-prose text-slate-700">
          {paragraph}
        </p>
      ))}
      <div className="mt-8 grid gap-8 md:grid-cols-2">
        <div>
          <h3 className="font-semibold text-slate-900">Near these {page.cityName} landmarks</h3>
          <ul className="mt-3 space-y-3 text-slate-700">
            {landmarks.map((landmark) => (
              <li key={landmark.name}>
                <strong>{landmark.name}</strong> — {landmark.context}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h3 className="font-semibold text-slate-900">Neighbourhoods and main intersections</h3>
          <ul className="mt-3 grid grid-cols-2 gap-x-4 gap-y-1 text-slate-700">
            {neighborhoods.map((name) => (
              <li key={name}>{name}</li>
            ))}
          </ul>
          <p className="mt-4 text-sm text-slate-600">Regular calls around {crossStreets.join('; ')}.</p>
        </div>
      </div>
    </section>
  );
}

/** Local project histories and verified testimonials. Unverified quotes are never rendered. */
export function LocalWork({ page }: { page: ServiceCityPage }) {
  const testimonials = page.testimonials.filter((t) => t.verified);
  if (!page.projects.length && !testimonials.length) return null;
  return (
    <section aria-labelledby="work-heading" className="py-12">
      <h2 id="work-heading" className="text-2xl font-semibold text-slate-900">
        Recent {page.serviceName.toLowerCase()} work in {page.cityName}
      </h2>
      <div className="mt-6 grid gap-6 md:grid-cols-2">
        {page.projects.map((project) => (
          <article key={project.title} className="rounded-lg border border-slate-200 p-5">
            <h3 className="font-semibold text-slate-900">{project.title}</h3>
            <div className="text-sm text-slate-500">
              {project.neighborhood}
              {project.date ? ` · ${project.date}` : ''}
            </div>
            <p className="mt-3 text-slate-700">{project.summary}</p>
          </article>
        ))}
        {testimonials.map((testimonial) => (
          <figure key={testimonial.quote.slice(0, 40)} className="rounded-lg bg-slate-50 p-5">
            <blockquote className="text-slate-800">“{testimonial.quote}”</blockquote>
            <figcaption className="mt-3 text-sm text-slate-600">
              {testimonial.author}
              {testimonial.neighborhood ? `, ${testimonial.neighborhood}` : ''}
              {testimonial.source === 'google' ? ' · Google review' : ''}
            </figcaption>
          </figure>
        ))}
      </div>
    </section>
  );
}

/** A real <table> with a caption and header cells, which AI crawlers parse reliably. */
export function ComparisonTable({ comparison }: { comparison: ServiceCityPage['comparison'] }) {
  return (
    <div className="mt-4 overflow-x-auto">
      <p className="max-w-prose text-slate-700">{comparison.summary}</p>
      <table className="mt-6 w-full min-w-[32rem] border-collapse text-left text-slate-700">
        <caption className="mb-3 text-left text-sm text-slate-500">{comparison.caption}</caption>
        <thead>
          <tr>
            {comparison.columns.map((column) => (
              <th key={column} scope="col" className="border-b-2 border-slate-900 px-3 py-2 font-semibold text-slate-900">
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {comparison.rows.map((row) => (
            <tr key={row[0]}>
              {row.map((cell, index) =>
                index === 0 ? (
                  <th key={cell} scope="row" className="border-b border-slate-200 px-3 py-2 font-medium text-slate-900">
                    {cell}
                  </th>
                ) : (
                  <td key={`${row[0]}-${index}`} className="border-b border-slate-200 px-3 py-2">
                    {cell}
                  </td>
                ),
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/**
 * Visible FAQ. Plain headings and paragraphs, not a JS accordion, so every
 * answer is in the server HTML. Pass the same array to faqPageJsonLd().
 */
export function FaqSection({ heading, items }: { heading: string; items: Array<{ q: string; a: string }> }) {
  return (
    <section aria-labelledby="faq-heading" className="py-12">
      <h2 id="faq-heading" className="text-2xl font-semibold text-slate-900">
        {heading}
      </h2>
      <div className="mt-6 space-y-6">
        {items.map((item) => (
          <div key={item.q}>
            <h3 className="font-semibold text-slate-900">{item.q}</h3>
            <p className="mt-2 max-w-prose text-slate-700">{item.a}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
