import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  build: {
    minify: 'esbuild',
    rollupOptions: {
      output: {
        entryFileNames: 'assets/index-e324a293.js'
      }
    }
  },
  server: {
    proxy: {
      '/web': {
        target: 'http://localhost:8217',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
