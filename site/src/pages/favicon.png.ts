// PNG favicon / apple-touch-icon (raster fallback Safari always renders).
import type { APIRoute } from 'astro';
import { renderFaviconPng } from '../lib/og.js';

export const GET: APIRoute = async () => {
  const png = await renderFaviconPng(180);
  return new Response(new Uint8Array(png), {
    headers: { 'Content-Type': 'image/png', 'Cache-Control': 'public, max-age=31536000' },
  });
};
