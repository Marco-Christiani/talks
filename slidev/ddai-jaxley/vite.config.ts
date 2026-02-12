import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    allowedHosts: [
      ".trycloudflare.com",
      "slides.datatician.io",
    ],
  },
})
