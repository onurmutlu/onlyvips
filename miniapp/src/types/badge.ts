// Rozet Türleri
export enum BadgeType {
  CONTENT_UNLOCK = 'content_unlock',  // İçerik açma rozeti
  ACHIEVEMENT = 'achievement',         // Başarı rozeti
  CREATOR = 'creator',                // İçerik üretici rozeti
  MEMBERSHIP = 'membership',          // Üyelik seviyesi rozeti
  EVENT = 'event',                    // Etkinlik rozeti
  SPECIAL = 'special'                 // Özel rozet
}

// Rozet Nadirlik Seviyeleri
export enum BadgeRarity {
  COMMON = 'common',      // Yaygın
  UNCOMMON = 'uncommon',  // Az yaygın
  RARE = 'rare',          // Nadir
  EPIC = 'epic',          // Epik
  LEGENDARY = 'legendary' // Efsanevi
}

// Rozet Arayüzü
export interface Badge {
  id: string;
  name: string;
  description: string;
  type: BadgeType;
  rarity: BadgeRarity;
  imageUrl: string;
  ipfsUrl?: string;       // NFT dönüşümü için IPFS linki
  mintable: boolean;      // NFT'ye dönüştürülebilir mi?
  mintDate?: number;      // NFT'ye dönüştürülme tarihi
  mintTxHash?: string;    // NFT mint işlem hash'i
  createdAt: number;
  unlockedAt?: number;
  relatedContentId?: string;
  relatedAchievementId?: string;
}

// Rozet mint durumunu kontrol eden fonksiyon
export const isBadgeMinted = (badge: Badge): boolean => {
  return badge.mintable && !!badge.mintDate && !!badge.ipfsUrl;
};

// IPFS URL oluşturma yardımcı fonksiyonu
export const generateMockIpfsUrl = (badgeId: string): string => {
  return `ipfs://Qm${Math.random().toString(36).substring(2, 15)}${Math.random().toString(36).substring(2, 15)}/${badgeId}`;
};

// Rozet başlangıç bilgileri
export const CONTENT_BADGES = {
  EARLY_SUPPORTER: {
    id: 'early_supporter',
    name: 'Erken Destekçi',
    description: 'OnlyVips platformunun erken destekçilerine verilen özel rozet.',
    type: BadgeType.SPECIAL,
    rarity: BadgeRarity.EPIC,
    imageUrl: '/assets/badges/early_supporter.png',
    mintable: true
  },
  VIP_ACCESS: {
    id: 'vip_access',
    name: 'VIP Erişimi',
    description: 'Özel içeriklere VIP erişiminiz olduğunu gösteren elit rozet.',
    type: BadgeType.MEMBERSHIP,
    rarity: BadgeRarity.RARE,
    imageUrl: '/assets/badges/vip_access.png',
    mintable: true
  },
  PREMIUM_CONTENT: {
    id: 'premium_content',
    name: 'Premium İçerik Rozeti',
    description: 'Premium içeriklere erişim sağladığınızı gösteren rozet.',
    type: BadgeType.CONTENT_UNLOCK,
    rarity: BadgeRarity.UNCOMMON,
    imageUrl: '/assets/badges/premium_content.png',
    mintable: true
  },
  CREATOR_SUPPORT: {
    id: 'creator_support',
    name: 'İçerik Üretici Destekçisi',
    description: 'İçerik üreticilerini desteklediğinizi gösteren rozet.',
    type: BadgeType.ACHIEVEMENT,
    rarity: BadgeRarity.COMMON,
    imageUrl: '/assets/badges/creator_support.png',
    mintable: false
  },
  CRYPTO_ENTHUSIAST: {
    id: 'crypto_enthusiast',
    name: 'Kripto Meraklısı',
    description: 'Blockchain teknolojilerine ilgi duyan kullanıcılara verilen rozet.',
    type: BadgeType.SPECIAL,
    rarity: BadgeRarity.UNCOMMON,
    imageUrl: '/assets/badges/crypto_enthusiast.png',
    mintable: true
  }
}; 