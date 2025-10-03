import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Badge, BadgeRarity, isBadgeMinted } from '../types/badge';
import { fetchUserBadges, mintBadgeAsNFT } from '../services/badgeService';
import { useUserStore } from '../stores/userStore';

const BadgePage: React.FC = () => {
  const navigate = useNavigate();
  const { telegramId } = useUserStore();
  
  const [badges, setBadges] = useState<Badge[]>([]);
  const [loading, setLoading] = useState(true);
  const [mintingBadgeId, setMintingBadgeId] = useState<string | null>(null);
  
  useEffect(() => {
    const loadBadges = async () => {
      if (!telegramId) return;
      
      try {
        setLoading(true);
        const badgesData = await fetchUserBadges(telegramId);
        setBadges(badgesData);
      } catch (error) {
        console.error('Rozetler yüklenirken hata oluştu:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadBadges();
  }, [telegramId]);
  
  // Rozeti NFT'ye dönüştür
  const handleMintBadge = async (badgeId: string) => {
    if (!telegramId) return;
    
    try {
      setMintingBadgeId(badgeId);
      const result = await mintBadgeAsNFT(badgeId, telegramId);
      
      if (result.success) {
        // Rozeti güncelle
        setBadges(prev => prev.map(badge => {
          if (badge.id === badgeId) {
            return {
              ...badge,
              ipfsUrl: result.ipfsUrl,
              mintDate: Date.now(),
              mintTxHash: result.txHash
            };
          }
          return badge;
        }));
        
        // Başarı mesajı göster
        const tg = window.Telegram?.WebApp;
        if (tg) {
          tg.showPopup({
            title: 'NFT Oluşturuldu!',
            message: 'Rozetiniz başarıyla NFT olarak oluşturuldu ve cüzdanınıza gönderildi.',
            buttons: [{ type: 'ok' }]
          });
        }
      }
    } catch (error) {
      console.error('Rozet NFT\'ye dönüştürülürken hata:', error);
    } finally {
      setMintingBadgeId(null);
    }
  };
  
  // Nadirlık seviyesine göre renk belirle
  const getRarityColor = (rarity: BadgeRarity) => {
    switch (rarity) {
      case BadgeRarity.COMMON:
        return 'border-gray-400 text-gray-300';
      case BadgeRarity.UNCOMMON:
        return 'border-green-400 text-green-300';
      case BadgeRarity.RARE:
        return 'border-blue-400 text-blue-300';
      case BadgeRarity.EPIC:
        return 'border-purple-400 text-purple-300';
      case BadgeRarity.LEGENDARY:
        return 'border-amber-400 text-amber-300';
      default:
        return 'border-gray-400 text-gray-300';
    }
  };
  
  // Tarih formatla
  const formatDate = (timestamp: number): string => {
    return new Date(timestamp).toLocaleDateString('tr-TR', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  };
  
  // Yükleme durumu
  if (loading) {
    return (
      <div className="min-h-screen pt-24 p-4 bg-gradient-to-br from-black via-gray-900 to-gray-800 text-white">
        <div className="container mx-auto max-w-md">
          <div className="flex items-center mb-6">
            <button 
              onClick={() => navigate('/')}
              className="mr-4 text-gray-400 hover:text-white transition-colors"
            >
              ← Geri
            </button>
            <h1 className="text-2xl font-bold text-white">Rozetlerim</h1>
          </div>
          
          <div className="grid grid-cols-2 gap-4 animate-pulse">
            {[1, 2, 3, 4].map(idx => (
              <div key={idx} className="bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-4">
                <div className="h-32 bg-gray-700/50 rounded-lg mb-3"></div>
                <div className="h-6 bg-gray-700/50 rounded w-2/3 mb-2"></div>
                <div className="h-4 bg-gray-700/50 rounded w-3/4"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen pt-24 p-4 pb-24 bg-gradient-to-br from-black via-gray-900 to-gray-800 text-white">
      <div className="container mx-auto max-w-md">
        <div className="flex items-center mb-6">
          <button 
            onClick={() => navigate('/')}
            className="mr-4 text-gray-400 hover:text-white transition-colors"
          >
            ← Geri
          </button>
          <h1 className="text-2xl font-bold text-white">Rozetlerim</h1>
        </div>
        
        {badges.length > 0 ? (
          <div className="grid grid-cols-2 gap-4">
            {badges.map(badge => {
              const isMinted = isBadgeMinted(badge);
              const rarityColor = getRarityColor(badge.rarity);
              
              return (
                <div 
                  key={badge.id}
                  className="bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-4 transition-transform hover:shadow-lg"
                >
                  <div className="relative mb-3">
                    <img 
                      src={badge.imageUrl} 
                      alt={badge.name}
                      className={`w-full aspect-square object-cover rounded-lg border-2 ${rarityColor}`}
                    />
                    
                    {/* Nadirlık etiketi */}
                    <div className={`absolute top-2 right-2 text-xs px-2 py-1 rounded-full bg-black/60 ${rarityColor}`}>
                      {badge.rarity}
                    </div>
                  </div>
                  
                  <h3 className="font-medium text-white mb-1">{badge.name}</h3>
                  <p className="text-gray-300 text-sm mb-2">{badge.description}</p>
                  
                  <div className="text-xs text-gray-400 mb-3">
                    Kazanıldı: {badge.unlockedAt ? formatDate(badge.unlockedAt) : 'Bilinmiyor'}
                  </div>
                  
                  {badge.mintable && (
                    <div>
                      {isMinted ? (
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-green-400">NFT oluşturuldu ✓</span>
                          <a 
                            href={badge.ipfsUrl} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-blue-400 underline"
                          >
                            IPFS Linki
                          </a>
                        </div>
                      ) : (
                        <button
                          onClick={() => handleMintBadge(badge.id)}
                          disabled={mintingBadgeId === badge.id}
                          className={`w-full py-2 px-3 rounded-lg text-xs font-medium transition-all
                            ${mintingBadgeId === badge.id
                              ? 'bg-indigo-900/40 text-indigo-400 cursor-wait'
                              : 'bg-indigo-600/80 text-white hover:bg-indigo-500/80'
                            }`}
                        >
                          {mintingBadgeId === badge.id ? 'İşleniyor...' : 'NFT\'ye Dönüştür'}
                        </button>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-6 text-center">
            <div className="text-4xl mb-2">🏆</div>
            <h3 className="text-xl font-medium text-white mb-2">Henüz Rozet Yok</h3>
            <p className="text-gray-400">
              Görevleri tamamlayarak ve içerikleri açarak rozetler kazanabilirsiniz.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default BadgePage; 