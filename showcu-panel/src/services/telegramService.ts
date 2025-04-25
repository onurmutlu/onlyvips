import { WebApp } from '@twa-dev/sdk';

export interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
  auth_date: number;
  hash: string;
}

export interface TelegramTheme {
  bg_color: string;
  text_color: string;
  hint_color: string;
  link_color: string;
  button_color: string;
  button_text_color: string;
}

export const telegramService = {
  getUser: (): TelegramUser | null => {
    return WebApp.initDataUnsafe.user || null;
  },

  isMiniApp: (): boolean => {
    return WebApp.isTelegram;
  },

  expand: (): void => {
    WebApp.expand();
  },

  showAlert: (message: string, callback?: () => void): void => {
    WebApp.showAlert(message, callback);
  },

  showConfirm: (message: string, callback?: (isConfirmed: boolean) => void): void => {
    WebApp.showConfirm(message, callback);
  },

  getTheme: (): TelegramTheme => {
    return WebApp.themeParams;
  },

  getPlatform: (): string => {
    return WebApp.platform;
  }
}; 