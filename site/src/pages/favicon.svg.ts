// Favicon as a build-time SVG, vectorized from the Fraunces § by Satori
// (font-independent, with intrinsic width/height — unlike a <text> SVG).
import type { APIRoute } from 'astro';
import { renderFaviconSvg } from '../lib/og.js';

export const GET: APIRoute = async () => {
  const svg = await renderFaviconSvg(64);
  return new Response(svg, {
    headers: { 'Content-Type': 'image/svg+xml', 'Cache-Control': 'public, max-age=31536000' },
  });
};
