import type { APIRoute } from 'astro';
import { listCards, portableMarkdown } from '../../../lib/cards.js';

export function getStaticPaths() {
  return listCards().map((c) => ({ params: { vendor: c.vendor, slug: c.slug }, props: c }));
}

export const GET: APIRoute = ({ props, site }) => {
  const { vendor, slug } = props as { vendor: string; slug: string };
  const base = import.meta.env.BASE_URL.replace(/\/$/, '');
  const origin = site ? new URL(site).origin : '';
  const md = portableMarkdown(vendor, slug, `${origin}${base}/cards/${vendor}/${slug}`);
  return new Response(md, {
    headers: { 'Content-Type': 'text/markdown; charset=utf-8' },
  });
};
