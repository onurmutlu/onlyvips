// Görev türleri
export enum TaskType {
  CONTENT_VIEW = 'content_view',       // İçerik görüntüleme
  CONTENT_PURCHASE = 'content_purchase', // İçerik satın alma
  REFERRAL = 'referral',              // Kullanıcı davet etme
  SOCIAL_SHARE = 'social_share',      // Sosyal medyada paylaşım
  COMMENT = 'comment',                // Yorum yapma
  APP_USAGE = 'app_usage',            // Uygulama kullanımı
  SUBSCRIPTION = 'subscription',      // Abonelik
  OTHER = 'other'                     // Diğer
}

// Görev durumu
export enum TaskStatus {
  PENDING = 'pending',       // Beklemede
  COMPLETED = 'completed',   // Tamamlandı
  VERIFIED = 'verified',     // Doğrulandı
  EXPIRED = 'expired',       // Süresi doldu
  FAILED = 'failed'          // Başarısız
}

// Görev doğrulama türü
export enum VerificationType {
  AUTOMATIC = 'automatic',    // Otomatik
  MANUAL = 'manual',          // Manuel
  BLOCKCHAIN = 'blockchain'   // Blockchain tabanlı
}

// Görev ödül türü
export enum RewardType {
  XP = 'xp',                 // Deneyim puanı
  TOKEN = 'token',           // Jeton
  BADGE = 'badge',           // Rozet
  CONTENT_ACCESS = 'content_access', // İçerik erişimi
  DISCOUNT = 'discount'      // İndirim
}

// Ödül arayüzü
export interface Reward {
  type: RewardType;
  amount: number;
  description?: string;
  badgeId?: string;
  contentId?: string;
}

// Görev arayüzü
export interface Task {
  id: string;
  title: string;
  description: string;
  type: TaskType;
  verificationMethod: VerificationType;
  rewards: Reward[];
  requiredActions?: {
    [key: string]: any;  // Göreve göre değişen gereksinimler
  };
  creatorId: string;
  createdAt: number;
  expiresAt?: number;
  maxCompletions?: number;
  currentCompletions?: number;
}

// Kullanıcı görevi
export interface UserTask {
  userId: string;
  taskId: string;
  status: TaskStatus;
  completedAt?: number;
  verifiedAt?: number;
  rewardsIssued: boolean;
}

// Telegram initData'dan referral kontrolü için helper fonksiyon
export const checkReferralFromTelegramData = (): string | null => {
  try {
    // Telegram WebApp verilerine eriş
    const tg = window.Telegram?.WebApp;
    
    if (!tg || !tg.initDataUnsafe || !tg.initDataUnsafe.start_param) {
      return null;
    }
    
    // start_param'ı kontrol et, referral_ ile başlıyorsa referral var demektir
    const startParam = tg.initDataUnsafe.start_param;
    if (startParam && startParam.startsWith('referral_')) {
      // referral_USER_ID formatında, USER_ID kısmını çıkart
      return startParam.split('_')[1] || null;
    }
    
    return null;
  } catch (error) {
    console.error('Telegram referral bilgisi çıkarılırken hata:', error);
    return null;
  }
}; 