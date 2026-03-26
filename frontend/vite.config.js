import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/upload': 'https://financeiq-bny8.onrender.com',
      '/stream': 'https://financeiq-bny8.onrender.com',
      '/report': 'https://financeiq-bny8.onrender.com',
      '/health': 'https://financeiq-bny8.onrender.com',
      '/auth': 'https://financeiq-bny8.onrender.com',
      '/chat': 'https://financeiq-bny8.onrender.com',
    }
  }
})
