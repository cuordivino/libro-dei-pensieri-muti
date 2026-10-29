import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// Se cambi account o nome del repository, aggiorna site e base.
export default defineConfig({
  site: 'https://cuordivino.github.io',
  base: '/libro-dei-pensieri-muti',
  trailingSlash: 'always',
  integrations: [sitemap({ filter: (p) => !p.includes('/admin/') })],
  build: { inlineStylesheets: 'auto' },
  prefetch: { prefetchAll: false, defaultStrategy: 'hover' },
});
