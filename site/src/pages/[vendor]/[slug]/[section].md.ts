import type { APIRoute } from 'astro';
import { listCards, sectionGroups, portableSectionMarkdown } from '../../../lib/cards.js';

// One markdown file per TOP-LEVEL section (owner-requested): the cards are
// long, and agents can fetch just the section they need instead of the whole
// card.md. Paths like /anthropic/claude-opus-5/6-alignment-assessment.md.
export function getStaticPaths() {
  return listCards().flatMap((c) =>
    sectionGroups(c.vendor, c.slug).map((g) => ({
      params: { vendor: c.vendor, slug: c.slug, section: g.slug },
      props: { vendor: c.vendor, slug: c.slug, group: g },
    })),
  );
}

export const GET: APIRoute = ({ props, site }) => {
  const { vendor, slug, group } = props as {
    vendor: string;
    slug: string;
    group: { title: string; slug: string; md: string; pages: number[] | null };
  };
  const base = import.meta.env.BASE_URL.replace(/\/$/, '');
  const origin = site ? new URL(site).origin : '';
  const md = portableSectionMarkdown(vendor, slug, group, `${origin}${base}/cards/${vendor}/${slug}`, {
    cardUrl: `${origin}${base}/${vendor}/${slug}/`,
    htmlUrl: `${origin}${base}/${vendor}/${slug}/`,
  });
  return new Response(md, {
    headers: { 'Content-Type': 'text/markdown; charset=utf-8' },
  });
};
