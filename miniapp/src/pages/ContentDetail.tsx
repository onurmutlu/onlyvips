import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../api/apiClient';
import { useTaskStore } from '../stores/taskStore';
import { useUserStore } from '../stores/userStore';

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
  requiredTaskId?: string;
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
  const [requiredTask, setRequiredTask] = useState<any>(null);
  const [taskStatus, setTaskStatus] = useState<'completed' | 'pending' | 'not_started'>('not_started');
  const [insufficientTokens, setInsufficientTokens] = useState(false);
  
  // Kullanıcı ID'sini al (gerçekte Telegram WebApp'ten alınacak)
  const userId = window.Telegram?.WebApp?.initDataUnsafe?.user?.id || 'demo-user';
  
  // Görev tamamlama için gerekli store fonksiyonlarını al
  const { completeTaskWithBackend, isTaskCompleted, tokens, spendTokens } = useUserStore();
  const { getTaskById } = useTaskStore();
  
  useEffect(() => {
    const loadContentData = async () => {
      if (!contentId) return;
      
      setLoading(true);
      try {
        // İçerik bilgilerini al
        const contentResponse = await api.content.getDetails(contentId, userId);
        
        if (contentResponse.success && contentResponse.data) {
          setContent(contentResponse.data);
          
          // İçerik için gereken görev varsa, görev bilgisini al
          if (contentResponse.data.requiredTaskId) {
            const taskResponse = await api.creators.getTaskById(contentResponse.data.requiredTaskId);
            
            if (taskResponse.success && taskResponse.data) {
              setRequiredTask(taskResponse.data);
              
              // Kullanıcının görevi tamamlayıp tamamlamadığını kontrol et
              const userTaskStatus = await api.user.getTaskStatus(userId, contentResponse.data.requiredTaskId);
              
              if (userTaskStatus.success && userTaskStatus.data) {
                setTaskStatus(userTaskStatus.data.status);
              }
            }
          }
          
          // Kullanıcı profili ve bakiyesini al
          if (userId) {
            const profileResponse = await api.user.getProfile(userId);
            if (profileResponse.data) {
              setIsSubscribed(
                profileResponse.data.subscriptions?.includes(contentResponse.data?.creator?.id || '')
              );
              setIsLiked(profileResponse.data.liked_content?.includes(contentId) || false);
            }
            
            const walletResponse = await api.user.getWallet(userId);
            if (walletResponse.data) {
              setUserBalance(walletResponse.data.balance || 0);
            }
          }
        } else {
          // Demo için
          setContent(getMockContent());
        }
      } catch (error) {
        console.error('İçerik bilgileri yüklenirken hata oluştu:', error);
        // Demo için
        setContent(getMockContent());
        setIsSubscribed(false);
        setIsLiked(false);
        setUserBalance(150);
      } finally {
        setLoading(false);
      }
    };
    
    loadContentData();
  }, [contentId, userId]);
  
  const handleContentPurchase = async () => {
    if (!content || !userId) return;
    
    // Kullanıcının yeterli token'ı olup olmadığını kontrol et
    if (tokens < (content.price || 0)) {
      setInsufficientTokens(true);
      setTimeout(() => setInsufficientTokens(false), 3000); // 3 saniye sonra bildirimi gizle
      return;
    }
    
    try {
      // Zustand store'dan token harcama işlevini çağır
      const success = spendTokens(content.price || 0);
      
      if (success) {
        setIsSubscribed(true);
        setPurchaseModalOpen(false);
        
        // Backend API'ye de bildir (opsiyonel)
        try {
          await api.packages.purchase(
            content.id, 
            userId, 
            'tokens'
          );
        } catch (error) {
          console.warn('Backend bildirimi gönderilirken hata:', error);
          // Backend bildirimi gönderilemese bile içerik erişimi açık kalır
        }
        
        // Başarılı mesajı göster
        alert('✅ İçerik başarıyla satın alındı!');
      } else {
        alert('❌ Token yetersiz. Daha fazla token kazanmak için görevleri tamamlayın.');
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
  
  const handleTaskComplete = async () => {
    if (!requiredTask) return;
    
    try {
      // UserStore'daki completeTaskWithBackend fonksiyonunu çağır
      const success = await completeTaskWithBackend(requiredTask.id);
      
      if (success) {
        setTaskStatus('completed');
        alert('✅ Görev başarıyla tamamlandı! Artık içeriği görüntüleyebilirsiniz.');
      } else {
        alert('❌ Görev tamamlanırken bir hata oluştu. Lütfen tekrar deneyin.');
      }
    } catch (error) {
      console.error('Görev tamamlama hatası:', error);
      alert('❌ İşlem sırasında bir hata oluştu.');
    }
  };
  
  // Görevin durumunu kontrol et (UserStore kullanarak)
  const checkTaskStatus = (taskId: string) => {
    if (isTaskCompleted(taskId)) {
      return 'completed';
    }
    return taskStatus;
  };
  
  // Demo için örnek içerik
  const getMockContent = (): ContentDetail => {
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
  
  // İçeriğin görev tamamlama gerektiği durumda içerik yerine görev bilgisi gösterme
  const renderContent = () => {
    // Eğer içerik için görev gerekmiyorsa normal içeriği göster
    if (!requiredTask) {
      return (
        <div className="content-detail-container">
          {/* İçerik Başlığı */}
          <div className="bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 p-6">
            <button
              className="mb-2 flex items-center text-white/80 hover:text-white"
              onClick={() => navigate(-1)}
            >
              ← Geri Dön
            </button>
            <h1 className="text-2xl font-bold">{content?.title}</h1>
            <div className="flex items-center mt-2">
              <Link to={`/creator/${content?.creator.id}`} className="flex items-center">
                <img
                  src={content?.creator.avatar}
                  alt={content?.creator.name}
                  className="w-8 h-8 rounded-full mr-2"
                />
                <span className="mr-1">{content?.creator.name}</span>
                {content?.creator.isVerified && (
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
                  {content?.isPremium && !isSubscribed ? (
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
                        
                        {/* Yetersiz token uyarısı */}
                        {insufficientTokens && (
                          <div className="bg-red-500/20 border border-red-500/30 text-red-300 p-3 rounded-lg mb-4 animate-pulse">
                            ⚠️ Yetersiz token! Daha fazla token kazanmak için görevleri tamamlayın.
                          </div>
                        )}
                        
                        <div className="flex flex-col items-center">
                          <div className="flex items-center gap-2 text-2xl font-bold mb-2">
                            <span className="text-pink-500">{content.price}</span>
                            <span className="text-yellow-500">★</span>
                            <span className="text-sm text-gray-300">/ {tokens} Token'ınız var</span>
                          </div>
                          <button
                            className={`px-6 py-2 rounded-full font-semibold ${
                              tokens >= (content.price || 0)
                                ? 'bg-gradient-to-r from-pink-500 to-purple-600 text-white hover:opacity-90'
                                : 'bg-gray-700 text-gray-400 cursor-not-allowed'
                            }`}
                            onClick={handleContentPurchase}
                          >
                            {tokens >= (content.price || 0) ? 'Şimdi Satın Al' : 'Yetersiz Token'}
                          </button>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div>
                      {/* İçerik türüne göre uygun görüntüleme */}
                      {content && content.mediaType === 'photo' && (
                        <img
                          src={content.mediaUrl}
                          alt={content.title}
                          className="w-full h-auto"
                        />
                      )}
                      
                      {content && content.mediaType === 'video' && (
                        <video
                          src={content.mediaUrl}
                          controls
                          poster={content.mediaThumbnail}
                          className="w-full h-auto"
                        />
                      )}
                      
                      {content && content.mediaType === 'audio' && (
                        <div className="p-6 flex flex-col items-center">
                          <div className="w-40 h-40 rounded-full bg-gradient-to-r from-pink-500 to-purple-600 flex items-center justify-center mb-4">
                            <span className="text-4xl">🎧</span>
                          </div>
                          <audio src={content.mediaUrl} controls className="w-full" />
                        </div>
                      )}
                      
                      {content && content.mediaType === 'text' && content.textContent && (
                        <div className="p-6">
                          <div className="prose prose-invert max-w-none">
                            {content.textContent}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                  
                  {/* İçerik Açıklaması ve Etkileşim Butonları */}
                  {content && (
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
                  )}
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
                  <Link to={`/creator/${content?.creator.id}`} className="flex items-center mb-4">
                    <img
                      src={content?.creator.avatar}
                      alt={content?.creator.name}
                      className="w-16 h-16 rounded-full mr-4 border-2 border-pink-500"
                    />
                    <div>
                      <div className="flex items-center">
                        <span className="font-semibold text-lg">{content?.creator.name}</span>
                        {content?.creator.isVerified && (
                          <span className="ml-1 text-blue-400">✓</span>
                        )}
                      </div>
                      <p className="text-gray-300 text-sm">{content?.creator.bio}</p>
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
                    {content?.relatedContent.map((item) => (
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
        </div>
      );
    }
    
    // Görev durumunu UserStore'dan kontrol et
    const currentTaskStatus = checkTaskStatus(requiredTask.id);
    
    // Eğer görev tamamlanmışsa normal içeriği göster
    if (currentTaskStatus === 'completed') {
      return (
        <div className="content-detail-container">
          {/* ... mevcut içerik gösterimi ... */}
        </div>
      );
    }
    
    // Eğer görev tamamlanmamışsa, görev bilgisi göster
    return (
      <div className="task-required-container">
        <div className="task-info-box">
          <div className="task-icon">🔒</div>
          <h2>Bu İçerik Kilitli</h2>
          <p>Bu içeriği görüntülemek için aşağıdaki görevi tamamlamanız gerekiyor:</p>
          
          <div className="task-card">
            <div className="task-type">
              {requiredTask.taskType === 'follow' && '👥 Takip Görevi'}
              {requiredTask.taskType === 'message' && '💬 Mesaj Görevi'}
              {requiredTask.taskType === 'watch' && '👁️ İzleme Görevi'}
            </div>
            <h3>{requiredTask.title}</h3>
            <div className="task-reward">
              <span className="reward-value">{requiredTask.reward}</span>
              <span className="reward-token">★</span>
              <span className="reward-text">Token Kazanacaksınız</span>
            </div>
            
            <button 
              className="complete-task-button"
              onClick={handleTaskComplete}
            >
              Görevi Tamamla
            </button>
          </div>
          
          <div className="other-actions">
            <Link to="/" className="back-link">Ana Sayfaya Dön</Link>
          </div>
        </div>
      </div>
    );
  };
  
  return (
    <div className="content-detail-page">
      {loading ? (
        <div className="loading-container">Yükleniyor...</div>
      ) : !content ? (
        <div className="error-container">
          <div className="error-message">İçerik bulunamadı</div>
          <button onClick={() => navigate(-1)} className="back-button">Geri Dön</button>
        </div>
      ) : (
        renderContent()
      )}
      
      {/* Satın Alma Modal */}
      {purchaseModalOpen && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-900 rounded-xl p-6 max-w-md w-full">
            <h3 className="text-xl font-bold mb-4">İçerik Satın Al</h3>
            <div className="mb-6">
              <div className="flex justify-between mb-2">
                <span>İçerik:</span>
                <span>{content?.title}</span>
              </div>
              <div className="flex justify-between mb-2">
                <span>Fiyat:</span>
                <span>{content?.price} Token</span>
              </div>
              <div className="flex justify-between mb-4">
                <span>Mevcut Token:</span>
                <span className={tokens < (content?.price || 0) ? 'text-red-500' : 'text-emerald-500'}>
                  {tokens} Token
                </span>
              </div>
              
              {tokens < (content?.price || 0) && (
                <div className="bg-red-900/50 text-red-300 p-3 rounded-lg mb-4">
                  Yetersiz token. Daha fazla token kazanmak için görevleri tamamlayın.
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
                disabled={tokens < (content?.price || 0)}
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