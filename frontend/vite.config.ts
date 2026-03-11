import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // GitHub Pages 部署到 /Noosphere/ 子路径
  base: '/Noosphere/',
  build: {
    outDir: 'dist',
  },
})
