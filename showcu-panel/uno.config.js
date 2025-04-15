import { defineConfig, presetUno, presetAttributify, presetIcons } from 'unocss';

export default defineConfig({
  presets: [
    presetUno(),
    presetAttributify(),
    presetIcons({
      scale: 1.2,
      collections: {
        mdi: () => import('@iconify-json/mdi/icons.json').then(i => i.default),
      }
    }),
  ],
  theme: {
    colors: {
      primary: 'var(--primary)',
      'primary-light': 'var(--primary-light)',
      'primary-dark': 'var(--primary-dark)',
      secondary: 'var(--secondary)',
      accent: 'var(--accent)',
      'bg-main': 'var(--bg-main)',
      'bg-card': 'var(--bg-card)',
      'bg-light': 'var(--bg-light)',
      'text-dark': 'var(--text-dark)',
      'text-light': 'var(--text-light)',
      'text-muted': 'var(--text-muted)',
      success: 'var(--success)',
      warning: 'var(--warning)',
      error: 'var(--error)',
      info: 'var(--info)',
    },
    shadows: {
      sm: 'var(--shadow-sm)',
      md: 'var(--shadow-md)',
      lg: 'var(--shadow-lg)',
    },
    borderRadius: {
      sm: 'var(--radius-sm)',
      md: 'var(--radius-md)',
      lg: 'var(--radius-lg)',
      full: 'var(--radius-full)',
    },
  },
  shortcuts: {
    'btn': 'py-2 px-4 rounded-full font-medium transition-all duration-300 focus:outline-none',
    'btn-primary': 'btn bg-gradient-to-r from-primary to-primary-light text-white hover:(shadow-lg -translate-y-1)',
    'btn-outline': 'btn border border-primary text-primary hover:(bg-primary text-white)',
    'btn-secondary': 'btn bg-secondary text-white hover:opacity-90',
    'card': 'bg-bg-card rounded-lg shadow-md p-4 border border-border-color',
    'input': 'w-full px-3 py-2 bg-opacity-10 bg-white border border-border-color rounded-lg focus:(outline-none ring-2 ring-primary border-transparent)',
    'label': 'block text-sm font-medium text-text-muted mb-1',
    'gradient-text': 'bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary-light',
    'backdrop-blur': 'backdrop-filter backdrop-blur-md bg-opacity-80',
  },
  rules: [
    ['bg-gradient-primary', { background: 'var(--gradient-primary)' }],
    ['bg-gradient-dark', { background: 'var(--gradient-dark)' }],
  ],
}); 