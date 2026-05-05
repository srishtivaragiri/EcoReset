import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    allowedHosts: ['ines-nondisposed-pursily.ngrok-free.dev'],
    proxy: {
      '/wipe': 'http://localhost:8000',
      '/status': 'http://localhost:8000',
      '/generate-cert': 'http://localhost:8000',
      '/api': 'http://localhost:8000',
      '/download': 'http://localhost:8000',
      '/download-qr': 'http://localhost:8000'
    }
  }
})