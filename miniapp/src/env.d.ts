/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_TELEGRAM_BOT_USERNAME: string;
  readonly VITE_TG_WEB_APP_VERSION: string;
  readonly VITE_TON_NETWORK: 'mainnet' | 'testnet';
  readonly VITE_MEDIA_URL: string;
  readonly VITE_SUPPORT_CHAT_URL: string;
  readonly VITE_FEATURE_FLAGS: string;
  readonly VITE_SENTRY_DSN: string;
  readonly VITE_NODE_ENV: 'development' | 'production' | 'test';
  readonly VITE_APP_VERSION: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
} 