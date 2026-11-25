import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// /api calls are proxied to the Flask backend, so no CORS setup is needed in development.
export default defineConfig({
  plugins: [react()],
  server: { proxy: { "/api": "http://localhost:5000" } },
});
