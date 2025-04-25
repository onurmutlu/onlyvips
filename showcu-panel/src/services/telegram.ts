import { WebApp } from '@twa-dev/sdk';

interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
  auth_date: number;
  hash: string;
}

class TelegramService {
  private user: TelegramUser | null = null;

  constructor() {
    this.initialize();
  }

  private initialize() {
    if (WebApp.initData) {
      this.user = WebApp.initDataUnsafe.user as TelegramUser;
    }
  }

  getUser(): TelegramUser | null {
    return this.user;
  }

  isTelegramWebApp(): boolean {
    return WebApp.platform !== 'unknown';
  }

  expand(): void {
    WebApp.expand();
  }

  close(): void {
    WebApp.close();
  }

  showAlert(message: string): void {
    WebApp.showAlert(message);
  }

  showConfirm(message: string): Promise<boolean> {
    return WebApp.showConfirm(message);
  }

  getTheme() {
    return WebApp.colorScheme;
  }

  getPlatform() {
    return WebApp.platform;
  }

  getViewport() {
    return {
      height: WebApp.viewportHeight,
      width: WebApp.viewportStableHeight,
    };
  }

  showPopup(params: {
    title?: string;
    message: string;
    buttons?: Array<{
      id: string;
      type?: 'default' | 'ok' | 'close' | 'cancel' | 'destructive';
      text: string;
    }>;
  }, callback?: (buttonId: string) => void) {
    WebApp.showPopup(params, callback);
  }

  setHeaderColor(color: string) {
    WebApp.setHeaderColor(color);
  }

  setBackgroundColor(color: string) {
    WebApp.setBackgroundColor(color);
  }

  enableClosingConfirmation() {
    WebApp.enableClosingConfirmation();
  }

  disableClosingConfirmation() {
    WebApp.disableClosingConfirmation();
  }
}

export const telegramService = new TelegramService(); 