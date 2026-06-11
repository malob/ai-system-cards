// Per-page Open Graph images, generated at build time. Astro turns each
// getStaticPaths entry into a real PNG on disk: /og/home.png and
// /og/<vendor>/<slug>.png. Referenced as og:image in Base.astro.
import type { APIRoute } from 'astro';
import { listCards, stitchedMarkdown } from '../../lib/cards.js';
import { renderOgPng } from '../../lib/og.js';

const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
  'August', 'September', 'October', 'November', 'December'];

// "2026-06-09" → "June 9, 2026" (manual, to dodge Date timezone shifts)
function fmtDate(d: string): string {
  const [y, m, day] = String(d).split('-').map(Number);
  return Number.isFinite(day) ? `${MONTHS[m - 1]} ${day}, ${y}` : String(d);
}

// total pages = highest page marker in the stitched markdown
function pageCount(vendor: string, slug: string): number {
  let max = 0;
  for (const m of stitchedMarkdown(vendor, slug).matchAll(/<!--\s*p\.(\d+)\s*-->/g)) {
    max = Math.max(max, Number(m[1]));
  }
  return max;
}

export function getStaticPaths() {
  const paths: Array<{ params: { path: string }; props: Record<string, unknown> }> = [
    { params: { path: 'home' }, props: { kind: 'home' } },
  ];
  for (const c of listCards()) {
    paths.push({
      params: { path: `${c.vendor}/${c.slug}` },
      props: {
        kind: 'card',
        title: c.meta.title,
        vendor: c.meta.vendor,
        date: fmtDate(String(c.meta.release_date)),
        pages: pageCount(c.vendor, c.slug),
      },
    });
  }
  return paths;
}

export const GET: APIRoute = async ({ props }) => {
  const png = await renderOgPng(props as Parameters<typeof renderOgPng>[0]);
  return new Response(new Uint8Array(png), {
    headers: { 'Content-Type': 'image/png', 'Cache-Control': 'public, max-age=31536000, immutable' },
  });
};
