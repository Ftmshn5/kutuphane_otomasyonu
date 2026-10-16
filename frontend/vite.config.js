import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Geliştirme sırasında /api isteklerini FastAPI'ye (8000) yönlendirir.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { "/api": "http://localhost:8000" },
  },
});
