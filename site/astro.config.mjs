import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://malob.github.io',
  base: '/ai-system-cards',
  trailingSlash: 'always',
  build: { format: 'directory' },
});
