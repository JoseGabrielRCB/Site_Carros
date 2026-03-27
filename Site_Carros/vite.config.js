import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  // --- ADICIONE O BLOCO ABAIXO ---
  server: {
    host: '0.0.0.0',      // Libera o acesso externo ao container
    port: 8080,           // Garante que o Vite use a porta mapeada no docker-compose
    strictPort: true,     // Se a 8080 estiver ocupada, ele trava em vez de mudar de porta
    watch: {
      usePolling: true,   // OBRIGATÓRIO para detectar mudanças no Windows/WSL
    },
    hmr: {
      clientPort: 8080,   // Corrige o erro de WebSocket no navegador
    },
  },
})