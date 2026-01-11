import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    hmr: {
      host: 'rickie-unaldermanly-jessenia.ngrok-free.dev',
      protocol: 'wss'
    }
  }
});
