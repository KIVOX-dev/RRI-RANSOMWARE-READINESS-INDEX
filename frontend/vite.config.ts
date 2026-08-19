import react from "@vitejs/plugin-react";
import path from "path";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { "@": path.resolve(__dirname, "./src") },
  },
  server: {
    host: true,
    port: 5173,
    watch: {
      // Docker Desktop on Windows doesn't reliably forward native filesystem
      // change events across the host<->container bind mount, so chokidar's
      // default inotify-based watch silently misses edits made from the
      // host. Polling guarantees changes are picked up.
      usePolling: true,
      interval: 300,
    },
  },
});
