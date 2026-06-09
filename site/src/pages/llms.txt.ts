import type { APIRoute } from 'astro';
import { listCards } from '../lib/cards.js';

export const GET: APIRoute = ({ site }) => {
  const base = import.meta.env.BASE_URL.replace(/\/$/, '');
  const origin = site ? new URL(site).origin : '';
  const root = `${origin}${base}`;
  const cards = listCards();
  const lines = [
    '# AI System Cards',
    '',
    '> A readable archive of AI model system cards, faithfully converted from the',
    '> original PDFs into markdown and HTML. Each card below links to its complete',
    '> markdown transcription (figures referenced by absolute URL).',
    '',
    '## Cards',
    '',
    ...cards.map(
      ({ vendor, slug, meta }) =>
        `- [${meta.title}](${root}/${vendor}/${slug}/card.md): ${meta.vendor}, ` +
        `${meta.release_date}. ${String(meta.description).replace(/\s+/g, ' ').trim()}`,
    ),
    '',
  ];
  return new Response(lines.join('\n'), {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
};
