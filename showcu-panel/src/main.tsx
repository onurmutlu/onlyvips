import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './index.css';
import 'virtual:uno.css';
import { initSentry } from './utils/sentry';

// Sentry hata izleme sistemini başlat
initSentry();

const container = document.getElementById('root');
if (!container) throw new Error('Failed to find the root element');
const root = createRoot(container);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
); 