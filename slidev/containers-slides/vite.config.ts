// FILE: vite.config.ts
// vite.config.ts
import { defineConfig } from 'vite'
import { fileURLToPath } from 'url'
import { dirname, resolve } from 'path'

const __dirname = dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  resolve: {
    alias: {
      '@lib': resolve(__dirname, './lib'),
    },
  },
  server: {
    allowedHosts: ['docker-workshop.com'],
  },
})
