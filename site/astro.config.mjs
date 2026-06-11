import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://malob.github.io',
  base: '/ai-system-cards',
  trailingSlash: 'always',
  build: { format: 'directory' },
  // only the HTML pages (home + cards, which end in '/'); excludes the
  // og/*.png, card.md, llms.txt, and 404.html routes
  integrations: [sitemap({ filter: (page) => page.endsWith('/') })],
});
