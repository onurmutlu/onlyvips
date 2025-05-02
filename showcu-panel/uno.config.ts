import { defineConfig, presetUno, presetAttributify, presetIcons } from 'unocss'

export default defineConfig({
  presets: [
    presetUno(),
    presetAttributify(),
    presetIcons({
      scale: 1.2,
      cdn: 'https://esm.sh/'
    })
  ],
  theme: {
    colors: {
      primary: '#0088cc',
      secondary: '#2c3e50',
      background: '#1a1a1a',
      text: '#ffffff',
      border: '#2d2d2d',
    },
    fontFamily: {
      sans: ['Inter', 'sans-serif'],
    },
  },
  shortcuts: {
    'btn': 'px-4 py-2 rounded-lg bg-primary text-white hover:bg-opacity-80 transition-colors',
    'input': 'px-4 py-2 rounded-lg bg-background border border-border text-text focus:outline-none focus:border-primary',
    'card': 'p-6 rounded-xl bg-background border border-border',
  },
}) 