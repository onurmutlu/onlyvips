import { useEffect, useState } from 'react';
import { telegramService } from '../services/telegramService';

export interface TelegramState {
  isMiniApp: boolean;
  theme: 'light' | 'dark';
  user: any;
  viewportHeight: number;
  viewportStableHeight: number;
}

export const useTelegram = () => {
  const [state, setState] = useState<TelegramState>({
    isMiniApp: false,
    theme: 'light',
    user: null,
    viewportHeight: 0,
    viewportStableHeight: 0,
  });

  useEffect(() => {
    const isMiniApp = telegramService.isMiniApp();
    const theme = telegramService.getTheme();
    const user = telegramService.getUser();
    const viewportHeight = telegramService.getViewportHeight();
    const viewportStableHeight = telegramService.getViewportStableHeight();

    setState({
      isMiniApp,
      theme,
      user,
      viewportHeight,
      viewportStableHeight,
    });

    const unsubscribeTheme = telegramService.onThemeChanged(() => {
      setState(prev => ({
        ...prev,
        theme: telegramService.getTheme(),
      }));
    });

    const unsubscribeViewport = telegramService.onViewportChanged((event) => {
      setState(prev => ({
        ...prev,
        viewportHeight: event.height,
        viewportStableHeight: event.isStateStable ? event.height : prev.viewportStableHeight,
      }));
    });

    return () => {
      unsubscribeTheme();
      unsubscribeViewport();
    };
  }, []);

  return state;
}; 