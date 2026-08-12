import sitemap from '@astrojs/sitemap';
import tailwindcss from '@tailwindcss/vite';
// @ts-check
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://wordapp.pages.dev', // change once Cloudflare Pages is setup
  integrations: [
    sitemap(),
  ],
  vite: {
    plugins: [tailwindcss()],
    build: {
      sourcemap: false,
    },
  },
});
