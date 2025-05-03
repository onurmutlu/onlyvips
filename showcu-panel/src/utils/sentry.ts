import * as Sentry from '@sentry/react';

/**
 * Sentry hata izleme sistemini başlatır
 */
export const initSentry = () => {
  // Sentry sadece üretim ortamında aktif olsun
  if (import.meta.env.PROD) {
    const dsn = import.meta.env.VITE_SENTRY_DSN;
    
    if (!dsn) {
      console.warn('Sentry DSN tanımlanmamış, hata izleme devre dışı.');
      return;
    }
    
    Sentry.init({
      dsn,
      environment: import.meta.env.MODE || 'development',
      integrations: [
        Sentry.reactRouterV6Integration({
          useEffect: React.useEffect,
          useLocation: React.useLocation,
          useNavigationType: React.useNavigationType,
          createRoutesFromChildren: React.createRoutesFromChildren,
          matchRoutes: React.matchRoutes,
        }),
        Sentry.replayIntegration(),
      ],
      // Performans izleme örnekleme oranı
      tracesSampleRate: 0.2,
      // Session izleme örnekleme oranı  
      replaysSessionSampleRate: 0.1,
      // Hata durumunda session izleme  
      replaysOnErrorSampleRate: 1.0,
      
      // Şovcu paneli için yayın versiyonu
      release: 'showcu-panel@' + (import.meta.env.VITE_APP_VERSION || '0.1.0'),
      
      // Profil bilgilerini topla (düşük oranda)
      profilesSampleRate: 0.05,
      
      // Kullanıcı bilgilerini filtrele
      beforeSend(event) {
        // Şovcu ID'sini anonimleştir
        if (event.user && event.user.id) {
          event.user.id = `creator-${event.user.id.substring(0, 2)}xxx`;
        }
        
        // İçerik bilgilerini filtrele
        if (event.extra) {
          // Hassas içerik bilgilerini temizle
          const sensitiveKeys = ['password', 'token', 'secret', 'credit_card', 'wallet'];
          for (const key of Object.keys(event.extra)) {
            if (sensitiveKeys.some(sk => key.toLowerCase().includes(sk))) {
              event.extra[key] = '[FILTERED]';
            }
          }
        }
        
        return event;
      },
    });
    
    console.log('Sentry hata izleme sistemine bağlandı - Şovcu Panel.');
  }
};

/**
 * Bir hatayı Sentry'ye raporlar
 * @param error Hata nesnesi
 * @param context Ek bağlam bilgisi
 */
export const reportError = (error: Error, context: Record<string, any> = {}) => {
  Sentry.captureException(error, {
    extra: context
  });
};

/**
 * Şovcu kullanıcı bilgisini ayarlar
 * @param showcuId Şovcu ID'si 
 * @param showcuName Şovcu ismi (zorunlu değil)
 */
export const setShowcuUser = (showcuId: string, showcuName?: string) => {
  Sentry.setUser({
    id: showcuId ? `creator-${showcuId.substring(0, 2)}xxx` : undefined,
    username: showcuName ? `creator-${showcuName.substring(0, 1)}xxx` : undefined,
  });
};

/**
 * Sentry breadcrumb (izleme noktası) ekler
 * @param message İzleme mesajı
 * @param category Kategori
 * @param data Ek veri
 */
export const addBreadcrumb = (
  message: string,
  category: string = 'showcu-panel',
  data: Record<string, any> = {}
) => {
  // Hassas verileri filtrele
  const filteredData = { ...data };
  const sensitiveKeys = ['password', 'token', 'secret', 'credit_card', 'wallet'];
  
  for (const key of Object.keys(filteredData)) {
    if (sensitiveKeys.some(sk => key.toLowerCase().includes(sk))) {
      filteredData[key] = '[FILTERED]';
    }
  }
  
  Sentry.addBreadcrumb({
    message,
    category,
    data: filteredData,
    level: 'info',
  });
};

export default {
  initSentry,
  reportError,
  setShowcuUser,
  addBreadcrumb,
}; 