/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_TON_CONNECT_MANIFEST_URL: string;
  readonly VITE_TON_RPC_URL: string;
  readonly VITE_TON_NETWORK: 'mainnet' | 'testnet';
  readonly VITE_MEDIA_URL: string;
  readonly VITE_TG_WEB_APP_VERSION: string;
  readonly VITE_SUPPORT_EMAIL: string;
  readonly VITE_ANALYTICS_ID: string;
  readonly VITE_SENTRY_DSN: string;
  readonly VITE_APP_VERSION: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
} 