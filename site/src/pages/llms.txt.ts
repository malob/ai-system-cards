import type { APIRoute } from 'astro';
import { listCards, sectionGroups } from '../lib/cards.js';

export const GET: APIRoute = ({ site }) => {
  const base = import.meta.env.BASE_URL.replace(/\/$/, '');
  const origin = site ? new URL(site).origin : '';
  const root = `${origin}${base}`;
  const cards = listCards();
  const lines = [
    '# AI System Cards',
    '',
    '> A readable archive of AI model system cards, faithfully converted from the',
    '> original PDFs into markdown and HTML. Each card links to its complete',
    '> markdown transcription; the nested entries are standalone per-section',
    '> markdown files — fetch just the section you need (figures referenced by',
    '> absolute URL).',
    '',
    '## Cards',
    '',
    ...cards.flatMap(({ vendor, slug, meta }) => [
      `- [${meta.title}](${root}/${vendor}/${slug}/card.md): ${meta.vendor}, ` +
        `${meta.release_date}. ${String(meta.description).replace(/\s+/g, ' ').trim()}`,
      ...sectionGroups(vendor, slug).map(
        (g) =>
          `  - [${g.title}](${root}/${vendor}/${slug}/${g.slug}.md)` +
          (g.pages ? `: pp. ${g.pages[0]}–${g.pages[1]}` : ''),
      ),
    ]),
    '',
  ];
  return new Response(lines.join('\n'), {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
};
