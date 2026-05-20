import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react({ jsxRuntime: 'classic' })],
  build: {
    outDir: '../src/refast_vtk_js/static',
    emptyOutDir: true,
    lib: {
      entry: resolve(__dirname, 'src/index.tsx'),
      name: 'RefastVtk',
      fileName: () => 'refast_vtk_js.js',
      formats: ['umd'],
    },
    rollupOptions: {
      // React and ReactDOM are provided globally by refast-client.js
      external: ['react', 'react-dom'],
      output: {
        globals: {
          react: 'React',
          'react-dom': 'ReactDOM',
        },
        name: 'RefastVtk',
        assetFileNames: 'refast_vtk_js[extname]',
        entryFileNames: 'refast_vtk_js.js',
      },
    },
    // Increase chunk size warning limit for VTK.js
    chunkSizeWarningLimit: 5000,
  },
  define: {
    'process.env.NODE_ENV': JSON.stringify('production'),
    'process.env': '{}',
  },
  optimizeDeps: {
    include: ['@kitware/vtk.js', 'react-vtk-js'],
  },
});
