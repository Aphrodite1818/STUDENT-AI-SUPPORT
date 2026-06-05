import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    allowedHosts: ["ferocious-stride-pug.ngrok-free.dev"],
    host: true,
    port: 5174,
    open: true,
  },
});
