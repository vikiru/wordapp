import type { APIRoute } from 'astro';

export const GET: APIRoute = () =>
  new Response(
    `User-agent: *\nAllow: /\n\nSitemap: ${new URL('/sitemap-index.xml', import.meta.env.SITE).href}\n`,
    { headers: { 'Content-Type': 'text/plain' } },
  );
