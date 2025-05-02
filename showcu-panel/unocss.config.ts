import { defineConfig, presetUno, presetAttributify, presetIcons } from 'unocss'

export default defineConfig({
  presets: [
    presetUno(),
    presetAttributify(),
    presetIcons({
      scale: 1.2,
      warn: true,
    }),
  ],
  theme: {
    colors: {
      primary: '#1890ff',
      success: '#52c41a',
      warning: '#faad14',
      error: '#f5222d',
      dark: '#141414',
    },
  },
  shortcuts: {
    'flex-center': 'flex items-center justify-center',
    'flex-between': 'flex items-center justify-between',
    'flex-col-center': 'flex flex-col items-center justify-center',
    'btn-primary': 'bg-primary text-white px-4 py-2 rounded-lg hover:bg-opacity-80 transition-all',
    'btn-success': 'bg-success text-white px-4 py-2 rounded-lg hover:bg-opacity-80 transition-all',
    'btn-warning': 'bg-warning text-white px-4 py-2 rounded-lg hover:bg-opacity-80 transition-all',
    'btn-error': 'bg-error text-white px-4 py-2 rounded-lg hover:bg-opacity-80 transition-all',
    'card': 'bg-white dark:bg-dark rounded-lg shadow-lg p-4',
    'input': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary',
  },
}) 