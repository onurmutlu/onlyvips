import { useEffect, useState } from 'react';

export const useTelegram = () => {
  const [tg, setTg] = useState(null);
  const [user, setUser] = useState(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    // Telegram WebApp API'sini kontrol et
    const telegram = window.Telegram?.WebApp;
    
    if (telegram) {
      // WebApp'i başlat
      telegram.ready();
      telegram.expand();

      // Kullanıcı bilgisini al
      const initData = telegram.initData || '';
      const initDataUnsafe = telegram.initDataUnsafe || {};
      
      setTg(telegram);
      setUser(initDataUnsafe?.user || null);
      setIsReady(true);
      
      // Ana uygulamaya hazır olduğunu bildir
      if (telegram.MainButton) {
        telegram.MainButton.hide();
      }
    } else {
      console.warn('Telegram WebApp API bulunamadı, geliştirme modunda çalışıyor.');
      
      // Geliştirme modunda taklit verisi
      setTg({
        ready: () => console.log('Telegram WebApp ready'),
        expand: () => console.log('Telegram WebApp expanded'),
        close: () => console.log('Telegram WebApp closed'),
        MainButton: {
          show: () => console.log('MainButton shown'),
          hide: () => console.log('MainButton hidden'),
          setText: (text) => console.log(`MainButton text set to: ${text}`),
          setParams: (params) => console.log('MainButton params set', params),
          onClick: (cb) => console.log('MainButton click handler set'),
          offClick: (cb) => console.log('MainButton click handler removed'),
        },
        BackButton: {
          show: () => console.log('BackButton shown'),
          hide: () => console.log('BackButton hidden'),
        },
        onEvent: (eventName, callback) => {
          console.log(`Event registered: ${eventName}`);
        },
        offEvent: (eventName, callback) => {
          console.log(`Event unregistered: ${eventName}`);
        },
        sendData: (data) => {
          console.log('Data sent to Telegram:', data);
        },
        hapticFeedback: {
          impactOccurred: (style) => console.log(`Haptic impact: ${style}`),
          notificationOccurred: (type) => console.log(`Haptic notification: ${type}`),
        }
      });
      
      // Geliştirme modu için test kullanıcısı
      setUser({
        id: 12345678,
        first_name: 'Test',
        last_name: 'Kullanıcı',
        username: 'showcu_test',
        language_code: 'tr',
        is_premium: true,
      });
      
      setIsReady(true);
    }
  }, []);

  return {
    tg,
    user,
    isReady,
  };
}; 