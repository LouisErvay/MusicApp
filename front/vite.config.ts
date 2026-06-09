import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  envPrefix: ['VITE_', 'API_'],
  server: {                             // Permet de rendre le serveur accessible depuis l'extérieur
    host: true,                         // Utilisé avec le téléphone en USB via `adb reverse tcp:port tcp:port`
  },
})
