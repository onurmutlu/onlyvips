import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUserStore } from '../stores/userStore';

// Token işlemi tipi
type TokenTransactionType = 
  | 'task_reward' 
  | 'content_purchase' 
  | 'referral_reward'
  | 'badge_mint'
  | 'level_up_bonus';

// Token işlemi arayüzü
interface TokenTransaction {
  id: string;
  amount: number;
  type: TokenTransactionType;
  title: string;
  description?: string;
  timestamp: number;
  relatedTaskId?: string;
  relatedContentId?: string;
}

const TokenHistory: React.FC = () => {
  const navigate = useNavigate();
  const { telegramId } = useUserStore();
  const [loading, setLoading] = useState(true);
  const [transactions, setTransactions] = useState<TokenTransaction[]>([]);
  
  useEffect(() => {
    const fetchTokenHistory = async () => {
      // Gerçek uygulamada backend'den veri çekilecek
      try {
        setLoading(true);
        
        // API'den token geçmişini çekme simülasyonu
        // Gerçek uygulamada, burada backend API çağrısı yapılacak
        setTimeout(() => {
          // Dummy veriler
          const mockTransactions: TokenTransaction[] = [
            {
              id: 'tx1',
              amount: 5,
              type: 'task_reward',
              title: 'Davet Görevi Tamamlandı',
              description: 'Yeni kullanıcı davet etme görevi başarıyla tamamlandı.',
              timestamp: Date.now() - 86400000 * 2, // 2 gün önce
              relatedTaskId: 'task123'
            },
            {
              id: 'tx2',
              amount: -10,
              type: 'content_purchase',
              title: 'İçerik Erişimi',
              description: 'Premium içeriğe erişim için token harcandı',
              timestamp: Date.now() - 86400000, // 1 gün önce
              relatedContentId: 'content456'
            },
            {
              id: 'tx3',
              amount: 20,
              type: 'referral_reward',
              title: 'Referans Bonusu',
              description: 'Davet ettiğiniz 2 kişi platforma katıldı',
              timestamp: Date.now() - 3600000 * 2, // 2 saat önce
            },
            {
              id: 'tx4',
              amount: 15,
              type: 'level_up_bonus',
              title: 'Seviye Atlama Bonusu',
              description: 'Seviye 3\'e ulaştığınız için bonus tokenler kazandınız',
              timestamp: Date.now() - 3600000, // 1 saat önce
            },
            {
              id: 'tx5',
              amount: 50,
              type: 'badge_mint',
              title: 'Elite Üye Rozeti Kazanıldı',
              description: 'Elite Kullanıcı rozetiniz için bonus tokenler',
              timestamp: Date.now() - 1800000, // 30 dakika önce
            }
          ];
          
          setTransactions(mockTransactions);
          setLoading(false);
        }, 800);
        
      } catch (error) {
        console.error("Token geçmişi yüklenirken hata oluştu:", error);
        setLoading(false);
      }
    };
    
    fetchTokenHistory();
  }, [telegramId]);
  
  // İşlem tipine göre ikon ve renk belirle
  const getTransactionMeta = (type: TokenTransactionType, amount: number) => {
    if (amount > 0) {
      // Kazanç
      switch (type) {
        case 'task_reward':
          return { icon: '🎯', color: 'text-emerald-400', bgColor: 'bg-emerald-900/30', borderColor: 'border-emerald-700/30' };
        case 'referral_reward':
          return { icon: '👥', color: 'text-blue-400', bgColor: 'bg-blue-900/30', borderColor: 'border-blue-700/30' };
        case 'level_up_bonus':
          return { icon: '⭐', color: 'text-amber-400', bgColor: 'bg-amber-900/30', borderColor: 'border-amber-700/30' };  
        case 'badge_mint':
          return { icon: '🏆', color: 'text-purple-400', bgColor: 'bg-purple-900/30', borderColor: 'border-purple-700/30' };
        default:
          return { icon: '💰', color: 'text-green-400', bgColor: 'bg-green-900/30', borderColor: 'border-green-700/30' };
      }
    } else {
      // Harcama
      return { icon: '🛒', color: 'text-red-400', bgColor: 'bg-red-900/30', borderColor: 'border-red-700/30' };
    }
  };
  
  // Tarih formatlama
  const formatDate = (timestamp: number) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString('tr-TR', { 
      day: 'numeric', 
      month: 'short', 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };
  
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
          <h1 className="text-2xl font-bold text-white">Token Geçmişi</h1>
        </div>
        
        {loading ? (
          <div className="flex flex-col space-y-4 animate-pulse">
            {[1, 2, 3, 4].map(idx => (
              <div key={idx} className="bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-4">
                <div className="h-6 bg-gray-700/50 rounded w-1/2 mb-2"></div>
                <div className="h-4 bg-gray-700/50 rounded w-3/4 mb-1"></div>
                <div className="h-4 bg-gray-700/50 rounded w-1/3"></div>
              </div>
            ))}
          </div>
        ) : (
          <>
            {transactions.length > 0 ? (
              <div className="space-y-4">
                {transactions.map(transaction => {
                  const { icon, color, bgColor, borderColor } = getTransactionMeta(transaction.type, transaction.amount);
                  
                  return (
                    <div 
                      key={transaction.id}
                      className={`${bgColor} ${borderColor} border rounded-xl p-4 shadow-md`}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex items-center">
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg ${bgColor} border ${borderColor}`}>
                            {icon}
                          </div>
                          <div className="ml-3">
                            <h3 className="font-medium text-white">{transaction.title}</h3>
                            {transaction.description && (
                              <p className="text-gray-300 text-sm mt-0.5">{transaction.description}</p>
                            )}
                            <div className="text-gray-400 text-xs mt-1">
                              {formatDate(transaction.timestamp)}
                            </div>
                          </div>
                        </div>
                        
                        <div className={`font-bold text-lg ${transaction.amount > 0 ? color : 'text-red-400'}`}>
                          {transaction.amount > 0 ? '+' : ''}{transaction.amount}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-6 text-center">
                <div className="text-4xl mb-2">🔍</div>
                <h3 className="text-xl font-medium text-white mb-2">Henüz işlem yok</h3>
                <p className="text-gray-400">
                  Görevleri tamamlayarak ve platform içinde etkileşimde bulunarak tokenler kazanabilirsiniz.
                </p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default TokenHistory; 