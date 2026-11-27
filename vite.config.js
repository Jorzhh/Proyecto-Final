import { defineConfig } from 'vite';
import { fileURLToPath } from 'node:url';

const projectRoot = fileURLToPath(new URL('./public/', import.meta.url));

export default defineConfig({
  root: projectRoot,
  base: './',
  publicDir: false,
  resolve: {
    alias: [{
      find: /^three$/,
      replacement: fileURLToPath(new URL('./node_modules/three/src/Three.js', import.meta.url))
    }]
  },
  server: { host: '127.0.0.1', port: 3006, strictPort: true },
  preview: { host: '127.0.0.1', port: 4173, strictPort: true },
  build: {
    outDir: fileURLToPath(new URL('./dist/', import.meta.url)),
    emptyOutDir: true,
    sourcemap: false,
    assetsDir: 'assets',
    target: 'es2018',
    rolldownOptions: {
      output: {
        codeSplitting: {
          groups: [
            { name: 'three-vendor', test: /[/\\]node_modules[/\\]three[/\\]/, priority: 20, maxSize: 400_000 },
            { name: 'chart-vendor', test: /[/\\]node_modules[/\\](chart\.js|@kurkle)[/\\]/, priority: 15 },
            { name: 'vendor', test: /[/\\]node_modules[/\\]/, priority: 10 }
          ]
        }
      }
    }
  }
});
