import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../api/apiClient';

interface ContentDetail {
  id: string;
  title: string;
  description: string;
  mediaType: 'photo' | 'video' | 'audio' | 'text';
  mediaUrl?: string;
  mediaThumbnail?: string;
  textContent?: string;
  likes: number;
  views: number;
  createdAt: string;
  isPremium: boolean;
  price?: number;
  creator: {
    id: string;
    name: string;
    avatar: string;
    bio: string;
    isVerified: boolean;
  };
  comments: Array<{
    id: string;
    userId: string;
    userName: string;
    userAvatar: string;
    text: string;
    createdAt: string;
  }>;
  relatedContent: Array<{
    id: string;
    title: string;
    thumbnail: string;
    isPremium: boolean;
  }>;
}

const ContentDetail: React.FC = () => {
  const { contentId } = useParams<{ contentId: string }>();
  const navigate = useNavigate();
  const [content, setContent] = useState<ContentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [comment, setComment] = useState('');
  const [isLiked, setIsLiked] = useState(false);
  const [purchaseModalOpen, setPurchaseModalOpen] = useState(false);
  const [userBalance, setUserBalance] = useState(0);
  
  // Kullanıcı ID'sini al (gerçekte Telegram WebApp'ten alınacak)
  const userId = window.Telegram?.WebApp?.initDataUnsafe?.user?.id || 'demo-user';
  
  useEffect(() => {
    const loadContentDetail = async () => {
      if (!contentId) return;
      
      setLoading(true);
      try {
        // İçerik detaylarını yükle
        const response = await api.content.getDetails(contentId);
        if (response.data) {
          setContent(response.data);
        } else {
          // Demo için
          setContent(getMockContentDetail());
        }
        
        // Kullanıcı profili ve bakiyesini al
        if (userId) {
          const profileResponse = await api.user.getProfile(userId);
          if (profileResponse.data) {
            setIsSubscribed(
              profileResponse.data.subscriptions?.includes(response.data?.creator?.id || '')
            );
            setIsLiked(profileResponse.data.liked_content?.includes(contentId) || false);
          }
          
          const walletResponse = await api.user.getWallet(userId);
          if (walletResponse.data) {
            setUserBalance(walletResponse.data.balance || 0);
          }
        }
      } catch (error) {
        console.error('İçerik yükleme hatası:', error);
        // Demo için
        setContent(getMockContentDetail());
        setIsSubscribed(false);
        setIsLiked(false);
        setUserBalance(150);
      } finally {
        setLoading(false);
      }
    };
    
    loadContentDetail();
  }, [contentId, userId]);
  
  const handleContentPurchase = async () => {
    if (!content || !userId) return;
    
    try {
      const response = await api.packages.purchase(
        content.id, 
        userId, 
        'stars'
      );
      
      if (response.data && response.data.success) {
        setIsSubscribed(true);
        setUserBalance(prev => prev - (content.price || 0));
        setPurchaseModalOpen(false);
        
        // Başarılı mesajı göster
        alert('✅ İçerik başarıyla satın alındı!');
      } else {
        alert('❌ Satın alma işlemi başarısız: ' + (response.data?.message || 'Bilinmeyen hata'));
      }
    } catch (error) {
      console.error('Satın alma hatası:', error);
      alert('❌ İşlem sırasında bir hata oluştu.');
    }
  };
  
  const handleLike = async () => {
    if (!content || !userId) return;
    
    try {
      await api.content.like(content.id, userId);
      setIsLiked(true);
      setContent(prev => {
        if (!prev) return null;
        return {
          ...prev,
          likes: prev.likes + 1
        };
      });
    } catch (error) {
      console.error('Beğenme hatası:', error);
    }
  };
  
  const handleCommentSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!comment.trim() || !content || !userId) return;
    
    try {
      await api.content.addComment(content.id, userId, comment);
      
      // Yeni yorum ekle (API'den güncel veriyi çekmek daha iyi olurdu)
      setContent(prev => {
        if (!prev) return null;
        
        // Yeni yorum nesnesi oluştur
        const newComment = {
          id: `temp-${Date.now()}`,
          userId,
          userName: 'Siz',
          userAvatar: 'https://i.pravatar.cc/150?img=1',
          text: comment,
          createdAt: new Date().toISOString()
        };
        
        return {
          ...prev,
          comments: [newComment, ...prev.comments]
        };
      });
      
      // Yorum alanını temizle
      setComment('');
    } catch (error) {
      console.error('Yorum ekleme hatası:', error);
    }
  };
  
  // Demo için örnek içerik
  const getMockContentDetail = (): ContentDetail => {
    return {
      id: contentId || 'mock-content',
      title: 'Plaj Günlüğü - Özel Çekim',
      description: 'Yaz tatilinde çektiğim en güzel fotoğraflar ve anılar. Bu özel koleksiyonu sadece VIP üyeler görebilir.',
      mediaType: 'photo',
      mediaUrl: 'https://picsum.photos/id/128/800/600',
      mediaThumbnail: 'https://picsum.photos/id/128/400/300',
      likes: 124,
      views: 342,
      createdAt: '2023-09-15T14:30:00Z',
      isPremium: true,
      price: 25,
      creator: {
        id: 'creator1',
        name: 'Aylin Sezer',
        avatar: 'https://i.pravatar.cc/150?img=29',
        bio: 'Model ve fotoğraf sanatçısı',
        isVerified: true
      },
      comments: [
        {
          id: 'comment1',
          userId: 'user1',
          userName: 'Mehmet K.',
          userAvatar: 'https://i.pravatar.cc/150?img=12',
          text: 'Harika fotoğraflar! Işık kullanımı çok profesyonelce.',
          createdAt: '2023-09-16T09:20:00Z'
        },
        {
          id: 'comment2',
          userId: 'user2',
          userName: 'Zeynep D.',
          userAvatar: 'https://i.pravatar.cc/150?img=25',
          text: 'En iyi koleksiyonun bu! Devamını bekliyorum 😍',
          createdAt: '2023-09-16T12:45:00Z'
        }
      ],
      relatedContent: [
        {
          id: 'related1',
          title: 'Yaz Esintisi',
          thumbnail: 'https://picsum.photos/id/152/300/200',
          isPremium: false
        },
        {
          id: 'related2',
          title: 'Deniz Kabukları',
          thumbnail: 'https://picsum.photos/id/143/300/200',
          isPremium: true
        },
        {
          id: 'related3',
          title: 'Gün Batımı',
          thumbnail: 'https://picsum.photos/id/129/300/200',
          isPremium: false
        }
      ]
    };
  };
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse text-pink-500 text-xl">Yükleniyor...</div>
      </div>
    );
  }
  
  if (!content) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-4">
        <div className="text-red-500 text-xl mb-4">İçerik bulunamadı</div>
        <button
          className="bg-pink-500 text-white px-4 py-2 rounded-lg"
          onClick={() => navigate('/')}
        >
          Ana Sayfaya Dön
        </button>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-gray-800 text-white pb-20">
      {/* İçerik Başlığı */}
      <div className="bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 p-6">
        <button
          className="mb-2 flex items-center text-white/80 hover:text-white"
          onClick={() => navigate(-1)}
        >
          ← Geri Dön
        </button>
        <h1 className="text-2xl font-bold">{content.title}</h1>
        <div className="flex items-center mt-2">
          <Link to={`/creator/${content.creator.id}`} className="flex items-center">
            <img
              src={content.creator.avatar}
              alt={content.creator.name}
              className="w-8 h-8 rounded-full mr-2"
            />
            <span className="mr-1">{content.creator.name}</span>
            {content.creator.isVerified && (
              <span className="text-blue-400 text-sm">✓</span>
            )}
          </Link>
        </div>
      </div>
      
      {/* İçerik Alanı */}
      <div className="container mx-auto p-4">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Ana İçerik */}
          <div className="lg:col-span-2">
            <div className="bg-black/30 rounded-xl overflow-hidden shadow-xl">
              {/* Premium içerik ve erişim kontrolü */}
              {content.isPremium && !isSubscribed ? (
                <div className="relative">
                  <img
                    src={content.mediaThumbnail || content.mediaUrl}
                    alt={content.title}
                    className="w-full h-80 object-cover blur-sm"
                  />
                  <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/70 p-6 text-center">
                    <div className="text-3xl mb-2">🔒</div>
                    <h3 className="text-xl font-bold mb-2">Premium İçerik</h3>
                    <p className="mb-4">
                      Bu içeriği görüntülemek için satın almanız gerekiyor.
                    </p>
                    <div className="flex flex-col items-center">
                      <div className="text-2xl font-bold text-pink-500 mb-2">
                        {content.price} Star
                      </div>
                      <button
                        className="bg-gradient-to-r from-pink-500 to-purple-600 px-6 py-2 rounded-full text-white font-semibold"
                        onClick={() => setPurchaseModalOpen(true)}
                      >
                        Şimdi Satın Al
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <div>
                  {/* İçerik türüne göre uygun görüntüleme */}
                  {content.mediaType === 'photo' && (
                    <img
                      src={content.mediaUrl}
                      alt={content.title}
                      className="w-full h-auto"
                    />
                  )}
                  
                  {content.mediaType === 'video' && (
                    <video
                      src={content.mediaUrl}
                      controls
                      poster={content.mediaThumbnail}
                      className="w-full h-auto"
                    />
                  )}
                  
                  {content.mediaType === 'audio' && (
                    <div className="p-6 flex flex-col items-center">
                      <div className="w-40 h-40 rounded-full bg-gradient-to-r from-pink-500 to-purple-600 flex items-center justify-center mb-4">
                        <span className="text-4xl">🎧</span>
                      </div>
                      <audio src={content.mediaUrl} controls className="w-full" />
                    </div>
                  )}
                  
                  {content.mediaType === 'text' && content.textContent && (
                    <div className="p-6">
                      <div className="prose prose-invert max-w-none">
                        {content.textContent}
                      </div>
                    </div>
                  )}
                </div>
              )}
              
              {/* İçerik Açıklaması ve Etkileşim Butonları */}
              <div className="p-6">
                <p className="text-gray-300 mb-6">{content.description}</p>
                
                <div className="flex justify-between items-center">
                  <div className="flex space-x-4">
                    {/* Beğenme butonu */}
                    <button
                      className={`flex items-center space-x-1 ${
                        isLiked ? 'text-pink-500' : 'text-gray-400 hover:text-pink-500'
                      }`}
                      onClick={handleLike}
                      disabled={isLiked}
                    >
                      <span>{isLiked ? '❤️' : '🤍'}</span>
                      <span>{content.likes}</span>
                    </button>
                    
                    {/* Görüntülenme */}
                    <div className="flex items-center space-x-1 text-gray-400">
                      <span>👁️</span>
                      <span>{content.views}</span>
                    </div>
                  </div>
                  
                  {/* Tarih */}
                  <div className="text-gray-400 text-sm">
                    {new Date(content.createdAt).toLocaleDateString('tr-TR')}
                  </div>
                </div>
              </div>
            </div>
            
            {/* Yorumlar */}
            <div className="mt-6 bg-black/30 rounded-xl p-6 shadow-xl">
              <h3 className="text-xl font-semibold mb-4">Yorumlar</h3>
              
              {/* Yorum form */}
              <form onSubmit={handleCommentSubmit} className="mb-6">
                <textarea
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  placeholder="Bir yorum yazın..."
                  className="w-full p-3 bg-black/50 border border-gray-700 rounded-lg text-white"
                  rows={3}
                />
                <div className="mt-2 flex justify-end">
                  <button
                    type="submit"
                    className="bg-pink-500 text-white px-4 py-2 rounded-lg"
                    disabled={!comment.trim()}
                  >
                    Yorum Ekle
                  </button>
                </div>
              </form>
              
              {/* Yorum listesi */}
              <div className="space-y-4">
                {content.comments.length > 0 ? (
                  content.comments.map((comment) => (
                    <div key={comment.id} className="border-b border-gray-800 pb-4">
                      <div className="flex items-start">
                        <img
                          src={comment.userAvatar}
                          alt={comment.userName}
                          className="w-10 h-10 rounded-full mr-3"
                        />
                        <div>
                          <div className="flex items-center">
                            <span className="font-semibold">{comment.userName}</span>
                            <span className="ml-2 text-gray-400 text-xs">
                              {new Date(comment.createdAt).toLocaleDateString('tr-TR')}
                            </span>
                          </div>
                          <p className="mt-1 text-gray-300">{comment.text}</p>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-400 text-center">Henüz yorum yapılmamış. İlk yorumu siz yapın!</p>
                )}
              </div>
            </div>
          </div>
          
          {/* Yan Panel */}
          <div className="lg:col-span-1">
            {/* Şovcu Bilgileri */}
            <div className="bg-black/30 rounded-xl p-6 shadow-xl mb-6">
              <h3 className="text-xl font-semibold mb-4">Şovcu</h3>
              <Link to={`/creator/${content.creator.id}`} className="flex items-center mb-4">
                <img
                  src={content.creator.avatar}
                  alt={content.creator.name}
                  className="w-16 h-16 rounded-full mr-4 border-2 border-pink-500"
                />
                <div>
                  <div className="flex items-center">
                    <span className="font-semibold text-lg">{content.creator.name}</span>
                    {content.creator.isVerified && (
                      <span className="ml-1 text-blue-400">✓</span>
                    )}
                  </div>
                  <p className="text-gray-300 text-sm">{content.creator.bio}</p>
                </div>
              </Link>
              
              {!isSubscribed && (
                <button className="w-full bg-gradient-to-r from-pink-500 to-purple-600 text-white py-2 rounded-lg">
                  Abone Ol
                </button>
              )}
            </div>
            
            {/* İlgili İçerikler */}
            <div className="bg-black/30 rounded-xl p-6 shadow-xl">
              <h3 className="text-xl font-semibold mb-4">Benzer İçerikler</h3>
              <div className="space-y-4">
                {content.relatedContent.map((item) => (
                  <Link
                    key={item.id}
                    to={`/content/${item.id}`}
                    className="flex items-center p-2 rounded-lg hover:bg-white/5"
                  >
                    <div className="w-20 h-16 relative overflow-hidden rounded-lg mr-3">
                      <img
                        src={item.thumbnail}
                        alt={item.title}
                        className="w-full h-full object-cover"
                      />
                      {item.isPremium && (
                        <div className="absolute top-1 right-1 bg-pink-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                          🔒
                        </div>
                      )}
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium text-white">{item.title}</h4>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Satın Alma Modal */}
      {purchaseModalOpen && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-900 rounded-xl p-6 max-w-md w-full">
            <h3 className="text-xl font-bold mb-4">İçerik Satın Al</h3>
            <div className="mb-6">
              <div className="flex justify-between mb-2">
                <span>İçerik:</span>
                <span>{content.title}</span>
              </div>
              <div className="flex justify-between mb-2">
                <span>Fiyat:</span>
                <span>{content.price} Star</span>
              </div>
              <div className="flex justify-between mb-4">
                <span>Mevcut Bakiye:</span>
                <span className={userBalance < (content.price || 0) ? 'text-red-500' : 'text-emerald-500'}>
                  {userBalance} Star
                </span>
              </div>
              
              {userBalance < (content.price || 0) && (
                <div className="bg-red-900/50 text-red-300 p-3 rounded-lg mb-4">
                  Yetersiz bakiye. Daha fazla Star satın almanız gerekiyor.
                </div>
              )}
            </div>
            
            <div className="flex justify-end space-x-2">
              <button
                className="px-4 py-2 bg-gray-700 text-white rounded-lg"
                onClick={() => setPurchaseModalOpen(false)}
              >
                İptal
              </button>
              <button
                className="px-4 py-2 bg-gradient-to-r from-pink-500 to-purple-600 text-white rounded-lg"
                onClick={handleContentPurchase}
                disabled={userBalance < (content.price || 0)}
              >
                Satın Al
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ContentDetail; 