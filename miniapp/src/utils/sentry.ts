import * as Sentry from '@sentry/react';

/**
 * Sentry hata izleme sistemini başlatır
 * @param environment Ortam adı (production, development, staging)
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
      environment: import.meta.env.VITE_NODE_ENV || 'development',
      integrations: [
        Sentry.reactRouterV6Integration(),
        Sentry.replayIntegration(),
      ],
      // Performans izleme örnekleme oranı
      tracesSampleRate: 0.2,
      // Session izleme örnekleme oranı  
      replaysSessionSampleRate: 0.1,
      // Hata durumunda session izleme  
      replaysOnErrorSampleRate: 1.0,
      
      // Uygulama hakkında ek bilgiler
      release: import.meta.env.VITE_APP_VERSION || '0.1.0',
      
      // Profil bilgilerini topla
      profilesSampleRate: 0.1,
      
      // Kullanıcı bilgisi toplamayı kapat
      beforeSend(event) {
        // Kullanıcı ID'sini anonim hale getir
        if (event.user) {
          event.user.id = `user-${Math.floor(Math.random() * 1000000)}`;
        }
        return event;
      },
    });
    
    console.log('Sentry hata izleme sistemine bağlandı.');
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
 * Kullanıcı kimliğini Sentry'de ayarlar (telegram kullanıcı ID'si gizlenir)
 * @param userId Kullanıcı ID'si 
 */
export const setUser = (userId: string) => {
  // Gerçek kullanıcı ID'sini Sentry'e gönderme
  const anonymousId = `user-${userId.substring(0, 2)}...${userId.substring(userId.length - 2)}`;
  
  Sentry.setUser({
    id: anonymousId,
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
  category: string = 'app',
  data: Record<string, any> = {}
) => {
  Sentry.addBreadcrumb({
    message,
    category,
    data,
    level: 'info',
  });
};

export default {
  initSentry,
  reportError,
  setUser,
  addBreadcrumb,
}; 