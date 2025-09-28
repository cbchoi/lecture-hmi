import { defineConfig } from 'vite'

export default defineConfig({
  root: 'src',
  server: {
    port: 5173,
    host: true,
    open: true,
    fs: {
      allow: ['..']
    }
  },
  build: {
    outDir: '../dist',
    assetsDir: 'assets'
  },
  publicDir: false
})