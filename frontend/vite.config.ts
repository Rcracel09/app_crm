import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { existsSync } from 'fs'

// Check if we're in Docker build context or local dev (same as app_draft)
const sharedPath = existsSync(path.resolve(__dirname, './shared'))
  ? path.resolve(__dirname, './shared')      // Docker: /app/shared
  : path.resolve(__dirname, '../../shared')  // Local: catalog_claudio/shared

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@shared': sharedPath
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true
      }
    }
  }
})