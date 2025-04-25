import { create } from 'zustand';
import { telegramService } from '../services';

interface TelegramState {
  user: {
    id: number;
    first_name: string;
    last_name?: string;
    username?: string;
    photo_url?: string;
    auth_date: number;
    hash: string;
  } | null;
  theme: 'light' | 'dark';
  platform: string;
  viewport: {
    height: number;
    width: number;
  };
  init: () => void;
  showAlert: (message: string, callback?: () => void) => void;
  showConfirm: (message: string, callback?: (isConfirmed: boolean) => void) => void;
  showPopup: (params: {
    title?: string;
    message: string;
    buttons?: Array<{
      id: string;
      type?: 'default' | 'ok' | 'close' | 'cancel' | 'destructive';
      text: string;
    }>;
  }, callback?: (buttonId: string) => void) => void;
  expand: () => void;
  close: () => void;
}

export const useTelegram = create<TelegramState>((set) => ({
  user: null,
  theme: 'light',
  platform: '',
  viewport: {
    height: 0,
    width: 0,
  },
  init: () => {
    telegramService.init();
    const user = telegramService.getUser();
    const theme = telegramService.getTheme();
    const platform = telegramService.getPlatform();
    const viewport = telegramService.getViewport();
    set({ user, theme: theme as 'light' | 'dark', platform, viewport });
  },
  showAlert: (message: string, callback?: () => void) => {
    telegramService.showAlert(message, callback);
  },
  showConfirm: (message: string, callback?: (isConfirmed: boolean) => void) => {
    telegramService.showConfirm(message, callback);
  },
  showPopup: (params: {
    title?: string;
    message: string;
    buttons?: Array<{
      id: string;
      type?: 'default' | 'ok' | 'close' | 'cancel' | 'destructive';
      text: string;
    }>;
  }, callback?: (buttonId: string) => void) => {
    telegramService.showPopup(params, callback);
  },
  expand: () => {
    telegramService.expand();
  },
  close: () => {
    telegramService.close();
  }
})); 