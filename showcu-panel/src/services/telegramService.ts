import WebApp from '@twa-dev/sdk';

export interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  language_code?: string;
  is_premium?: boolean;
  added_to_attachment_menu?: boolean;
  allows_write_to_pm?: boolean;
}

export type TelegramTheme = 'light' | 'dark';

// Dummy data for non-Telegram browser testing
const dummyUser: TelegramUser = {
  id: 123456789,
  first_name: 'Test',
  last_name: 'User',
  username: 'testuser',
  language_code: 'tr',
  is_premium: true,
  added_to_attachment_menu: true,
  allows_write_to_pm: true
};

class TelegramService {
  init() {
    WebApp.ready();
    WebApp.setHeaderColor('#0088cc');
    WebApp.setBackgroundColor('#1a1a1a');
    WebApp.expand();
  }

  getUser() {
    return WebApp.initDataUnsafe.user;
  }

  getTheme() {
    return WebApp.colorScheme;
  }

  getPlatform() {
    return WebApp.platform;
  }

  isExpanded() {
    return WebApp.isExpanded;
  }

  expand() {
    WebApp.expand();
  }

  showAlert(message: string) {
    WebApp.showAlert(message);
  }

  showConfirm(message: string) {
    return WebApp.showConfirm(message);
  }

  isMiniApp() {
    return WebApp.isVersionAtLeast('6.0');
  }

  getViewportHeight() {
    return WebApp.viewportHeight;
  }

  getViewportStableHeight() {
    return WebApp.viewportStableHeight;
  }

  getHeaderColor() {
    return WebApp.headerColor;
  }

  getBackgroundColor() {
    return WebApp.backgroundColor;
  }

  getMainButton() {
    return WebApp.MainButton;
  }

  getBackButton() {
    return WebApp.BackButton;
  }

  getHapticFeedback() {
    return WebApp.HapticFeedback;
  }

  getVersion() {
    return WebApp.version;
  }

  getInitData() {
    return WebApp.initData;
  }

  getInitDataUnsafe() {
    return WebApp.initDataUnsafe;
  }

  isClosingConfirmationEnabled() {
    return WebApp.isClosingConfirmationEnabled;
  }

  setClosingConfirmation(enabled: boolean) {
    if (enabled) {
      WebApp.enableClosingConfirmation();
    } else {
      WebApp.disableClosingConfirmation();
    }
  }

  setBackButton(isVisible: boolean) {
    if (isVisible) {
      WebApp.BackButton.show();
    } else {
      WebApp.BackButton.hide();
    }
  }

  setMainButton(params: { text: string; color?: string; textColor?: string; isVisible?: boolean; isActive?: boolean; isProgressVisible?: boolean }) {
    const { text, color, textColor, isVisible, isActive, isProgressVisible } = params;
    WebApp.MainButton.text = text;
    if (color) WebApp.MainButton.color = color;
    if (textColor) WebApp.MainButton.textColor = textColor;
    if (isVisible) WebApp.MainButton.show();
    if (isActive) WebApp.MainButton.enable();
    if (isProgressVisible) WebApp.MainButton.showProgress();
  }

  onMainButtonClick(callback: () => void) {
    WebApp.MainButton.onClick(callback);
    return () => WebApp.MainButton.offClick(callback);
  }

  onBackButtonClick(callback: () => void) {
    WebApp.BackButton.onClick(callback);
    return () => WebApp.BackButton.offClick(callback);
  }

  onViewportChanged(callback: (event: { isStateStable: boolean }) => void) {
    WebApp.onEvent('viewportChanged', callback);
    return () => WebApp.offEvent('viewportChanged', callback);
  }

  onThemeChanged(callback: () => void) {
    WebApp.onEvent('themeChanged', callback);
    return () => WebApp.offEvent('themeChanged', callback);
  }

  onMainButtonClicked(callback: () => void) {
    WebApp.onEvent('mainButtonClicked', callback);
    return () => WebApp.offEvent('mainButtonClicked', callback);
  }

  onBackButtonClicked(callback: () => void) {
    WebApp.onEvent('backButtonClicked', callback);
    return () => WebApp.offEvent('backButtonClicked', callback);
  }

  onInvoiceClosed(callback: (event: { url: string; status: 'paid' | 'cancelled' | 'failed' | 'pending' }) => void) {
    WebApp.onEvent('invoiceClosed', callback);
    return () => WebApp.offEvent('invoiceClosed', callback);
  }

  onPopupClosed(callback: (event: { button_id: string | null }) => void) {
    WebApp.onEvent('popupClosed', callback);
    return () => WebApp.offEvent('popupClosed', callback);
  }

  onQrTextReceived(callback: (event: { data?: string }) => void) {
    WebApp.onEvent('qrTextReceived', callback);
    return () => WebApp.offEvent('qrTextReceived', callback);
  }

  onClipboardTextReceived(callback: (event: { data?: string }) => void) {
    WebApp.onEvent('clipboardTextReceived', callback);
    return () => WebApp.offEvent('clipboardTextReceived', callback);
  }

  onWriteAccessRequested(callback: (event: { status: 'allowed' | 'cancelled' }) => void) {
    WebApp.onEvent('writeAccessRequested', callback);
    return () => WebApp.offEvent('writeAccessRequested', callback);
  }

  onContactRequested(callback: (event: { status: 'sent' | 'cancelled' }) => void) {
    WebApp.onEvent('contactRequested', callback);
    return () => WebApp.offEvent('contactRequested', callback);
  }
}

export const telegramService = new TelegramService(); 