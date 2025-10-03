import { Badge, BadgeType, BadgeRarity, CONTENT_BADGES, generateMockIpfsUrl } from '../types/badge';
import api from '../api/apiClient';

// Kullanıcının rozetlerini yükle
export const fetchUserBadges = async (userId: string): Promise<Badge[]> => {
  try {
    // Gerçek API çağrısı
    const response = await api.badges.getUserBadges(userId);
    if (response.success && response.data) {
      return response.data;
    }
    
    // Fallback - Demo veriler
    return getDemoBadges();
  } catch (error) {
    console.error('Rozetler yüklenirken hata oluştu:', error);
    // Hata durumunda boş dizi döndür
    return [];
  }
};

// İçerik açıldığında rozet kazanma
export const unlockContentBadge = async (
  userId: string, 
  contentId: string,
  contentTitle: string,
  contentType: string
): Promise<Badge | null> => {
  try {
    // Gerçek API çağrısı
    const response = await api.badges.unlockContentBadge(userId, contentId);
    
    if (response.success && response.data) {
      return response.data;
    }
    
    // Fallback - Demo rozet döndür
    return createMockContentBadge(contentId, contentTitle, contentType);
  } catch (error) {
    console.error('Rozet açılırken hata oluştu:', error);
    return null;
  }
};

// Rozeti NFT'ye dönüştür
export const mintBadgeAsNFT = async (badgeId: string, userId: string): Promise<{ success: boolean; ipfsUrl?: string; txHash?: string }> => {
  try {
    // Gerçek API çağrısı
    const response = await api.badges.mintBadge(badgeId, userId);
    
    if (response.success) {
      return {
        success: true,
        ipfsUrl: response.data?.ipfsUrl,
        txHash: response.data?.txHash
      };
    }
    
    // Fallback - Demo IPFS ve işlem hash'i oluştur
    const ipfsUrl = generateMockIpfsUrl(badgeId);
    const txHash = `0x${Math.random().toString(36).substring(2, 15)}${Math.random().toString(36).substring(2, 15)}`;
    
    return {
      success: true,
      ipfsUrl,
      txHash
    };
  } catch (error) {
    console.error('Rozet NFT\'ye dönüştürülürken hata oluştu:', error);
    return { success: false };
  }
};

// İçerik türüne göre rozet seçimi
const selectBadgeTypeForContent = (contentType: string): Badge => {
  switch(contentType.toLowerCase()) {
    case 'premium':
      return {
        ...CONTENT_BADGES.PREMIUM_CONTENT,
        createdAt: Date.now()
      };
    case 'vip':
      return {
        ...CONTENT_BADGES.VIP_ACCESS,
        createdAt: Date.now()
      };
    case 'exclusive':
      return {
        ...CONTENT_BADGES.CRYPTO_ENTHUSIAST,
        createdAt: Date.now()
      };
    default:
      return {
        ...CONTENT_BADGES.CREATOR_SUPPORT,
        createdAt: Date.now()
      };
  }
};

// İçerik rozeti oluştur
const createMockContentBadge = (contentId: string, contentTitle: string, contentType: string): Badge => {
  const baseBadge = selectBadgeTypeForContent(contentType);
  
  return {
    ...baseBadge,
    id: `${baseBadge.id}_${contentId}`,
    name: `${baseBadge.name}: ${contentTitle}`,
    description: `${contentTitle} içeriğine erişim sağlayarak kazanılan rozet.`,
    relatedContentId: contentId,
    unlockedAt: Date.now()
  };
};

// Demo rozetleri
const getDemoBadges = (): Badge[] => {
  return [
    {
      ...CONTENT_BADGES.EARLY_SUPPORTER,
      id: 'early_supporter_123',
      createdAt: Date.now() - 1000 * 60 * 60 * 24 * 7, // 1 hafta önce
      unlockedAt: Date.now() - 1000 * 60 * 60 * 24 * 7
    },
    {
      ...CONTENT_BADGES.PREMIUM_CONTENT,
      id: 'premium_content_456',
      name: 'Premium İçerik Rozeti: VIP Rehberi',
      description: 'VIP Rehberi içeriğine erişim sağlayarak kazanılan rozet.',
      createdAt: Date.now() - 1000 * 60 * 60 * 24 * 3, // 3 gün önce
      unlockedAt: Date.now() - 1000 * 60 * 60 * 24 * 3,
      relatedContentId: 'content_456'
    }
  ];
}; 