import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/apiClient';
import ContentCard from '../components/ContentCard';

interface Creator {
  id: string;
  name: string;
  bio: string;
  avatar: string;
  coverImage: string;
  isVerified: boolean;
  isOnline?: boolean;
  joinDate: string;
  socialLinks: {
    instagram?: string;
    twitter?: string;
    website?: string;
  };
  statistics: {
    contentCount: number;
    subscriberCount: number;
    likes: number;
    views: number;
  };
  tags: string[];
}

interface Package {
  id: string;
  name: string;
  description: string;
  price: number;
  duration: string;
  benefits: string[];
  featuredContent?: {
    id: string;
    title: string;
    thumbnail: string;
  };
  isPopular?: boolean;
}

interface Content {
  id: string;
  title: string;
  thumbnail: string;
  creatorName: string;
  creatorId: string;
  creatorAvatar: string;
  price?: number;
  isPremium: boolean;
  likes: number;
  category: string;
  previewText?: string;
}

const CreatorProfile: React.FC = () => {
  const { creatorId } = useParams<{ creatorId: string }>();
  const navigate = useNavigate();
  const [creator, setCreator] = useState<Creator | null>(null);
  const [packages, setPackages] = useState<Package[]>([]);
  const [contents, setContents] = useState<Content[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'content' | 'packages'>('content');
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [userBalance, setUserBalance] = useState(0);
  const [subscribeModalOpen, setSubscribeModalOpen] = useState(false);
  const [selectedPackage, setSelectedPackage] = useState<Package | null>(null);
  
  // Kullanıcı ID'sini al (gerçekte Telegram WebApp'ten alınacak)
  const userId = window.Telegram?.WebApp?.initDataUnsafe?.user?.id || 'demo-user';
  
  useEffect(() => {
    const loadCreatorData = async () => {
      if (!creatorId) return;
      
      setLoading(true);
      try {
        // Şovcu bilgilerini al
        const creatorResponse = await api.creators.getProfile(creatorId);
        if (creatorResponse.data) {
          setCreator(creatorResponse.data);
        } else {
          // Demo için
          setCreator(getMockCreator());
        }
        
        // İçerikleri al
        const contentResponse = await api.creators.getContent(creatorId);
        if (contentResponse.data && contentResponse.data.content) {
          setContents(contentResponse.data.content);
        } else {
          // Demo için
          setContents(getMockContent());
        }
        
        // Paketleri al
        const packagesResponse = await api.packages.getByCreator(creatorId);
        if (packagesResponse.data && packagesResponse.data.packages) {
          setPackages(packagesResponse.data.packages);
        } else {
          // Demo için
          setPackages(getMockPackages());
        }
        
        // Kullanıcı profili ve bakiyesini al
        if (userId) {
          const profileResponse = await api.user.getProfile(userId);
          if (profileResponse.data) {
            setIsSubscribed(
              profileResponse.data.subscriptions?.includes(creatorId) || false
            );
          }
          
          const walletResponse = await api.user.getWallet(userId);
          if (walletResponse.data) {
            setUserBalance(walletResponse.data.balance || 0);
          }
        }
      } catch (error) {
        console.error('Şovcu bilgileri yüklenirken hata oluştu:', error);
        // Demo için
        setCreator(getMockCreator());
        setContents(getMockContent());
        setPackages(getMockPackages());
        setIsSubscribed(false);
        setUserBalance(150);
      } finally {
        setLoading(false);
      }
    };
    
    loadCreatorData();
  }, [creatorId, userId]);
  
  const handleContentClick = (contentId: string) => {
    navigate(`/content/${contentId}`);
  };
  
  const handleSubscribe = (packageItem: Package) => {
    setSelectedPackage(packageItem);
    setSubscribeModalOpen(true);
  };
  
  const handleSubscribeConfirm = async () => {
    if (!selectedPackage || !creator || !userId) return;
    
    try {
      const response = await api.creators.subscribe(
        creator.id,
        userId,
        selectedPackage.id
      );
      
      if (response.data && response.data.success) {
        setIsSubscribed(true);
        setUserBalance(prev => prev - (selectedPackage.price || 0));
        setSubscribeModalOpen(false);
        
        // Başarılı mesajı göster
        alert(`✅ ${creator.name} kanalına başarıyla abone oldunuz!`);
      } else {
        alert('❌ Abonelik işlemi başarısız: ' + (response.data?.message || 'Bilinmeyen hata'));
      }
    } catch (error) {
      console.error('Abonelik hatası:', error);
      alert('❌ İşlem sırasında bir hata oluştu.');
    }
  };
  
  // Demo için mock veriler
  const getMockCreator = (): Creator => {
    return {
      id: creatorId || 'mock-creator',
      name: 'Aylin Sezer',
      bio: 'Model ve fotoğraf sanatçısı. Özel çekimler, koleksiyonlar ve kişisel hikayelerimi paylaşıyorum. Her gün yeni içeriklerle karşınızdayım.',
      avatar: 'https://i.pravatar.cc/150?img=29',
      coverImage: 'https://picsum.photos/id/22/1200/400',
      isVerified: true,
      isOnline: true,
      joinDate: '2023-06-15T10:00:00Z',
      socialLinks: {
        instagram: 'aylinsezer',
        twitter: 'aylinsezermodel'
      },
      statistics: {
        contentCount: 42,
        subscriberCount: 1250,
        likes: 7845,
        views: 28560
      },
      tags: ['model', 'fotoğraf', 'moda', 'seyahat', 'lifestyle']
    };
  };
  
  const getMockContent = (): Content[] => {
    return [
      {
        id: 'content1',
        title: 'Moda Çekimi - Yaz Koleksiyonu',
        thumbnail: 'https://picsum.photos/id/91/600/400',
        creatorName: 'Aylin Sezer',
        creatorId: creatorId || 'creator1',
        creatorAvatar: 'https://i.pravatar.cc/150?img=29',
        price: 15,
        isPremium: true,
        likes: 124,
        category: 'photo',
        previewText: 'Yeni yaz koleksiyonum ile çok özel pozlar...'
      },
      {
        id: 'content2',
        title: 'Tatil Günlüğü - Bodrum',
        thumbnail: 'https://picsum.photos/id/167/600/400',
        creatorName: 'Aylin Sezer',
        creatorId: creatorId || 'creator1',
        creatorAvatar: 'https://i.pravatar.cc/150?img=29',
        isPremium: false,
        likes: 98,
        category: 'photo'
      },
      {
        id: 'content3',
        title: 'Akşam Meditasyonu - ASMR',
        thumbnail: 'https://picsum.photos/id/193/600/400',
        creatorName: 'Aylin Sezer',
        creatorId: creatorId || 'creator1',
        creatorAvatar: 'https://i.pravatar.cc/150?img=29',
        price: 10,
        isPremium: true,
        likes: 76,
        category: 'audio',
        previewText: 'Rahatlatıcı sesler ve fısıltılar...'
      },
      {
        id: 'content4',
        title: 'Moda Haftası Arkası',
        thumbnail: 'https://picsum.photos/id/128/600/400',
        creatorName: 'Aylin Sezer',
        creatorId: creatorId || 'creator1',
        creatorAvatar: 'https://i.pravatar.cc/150?img=29',
        isPremium: false,
        likes: 64,
        category: 'video'
      }
    ];
  };
  
  const getMockPackages = (): Package[] => {
    return [
      {
        id: 'package1',
        name: 'Standart VIP',
        description: 'Tüm premium içeriklere erişim ve özel mesajlaşma hakkı.',
        price: 50,
        duration: '1 ay',
        benefits: [
          'Tüm premium içeriklere erişim',
          'Özel mesajlaşma hakkı',
          'Yeni içeriklerden haberdar olma'
        ],
        featuredContent: {
          id: 'content1',
          title: 'Moda Çekimi - Yaz Koleksiyonu',
          thumbnail: 'https://picsum.photos/id/91/300/200'
        }
      },
      {
        id: 'package2',
        name: 'Premium VIP',
        description: 'Ekstra özel içerikler ve öncelikli cevaplama hakkı ile tam erişim.',
        price: 100,
        duration: '1 ay',
        benefits: [
          'Tüm premium içeriklere erişim',
          'Ekstra özel içerikler',
          'Özel mesajlaşma hakkı',
          'Öncelikli cevaplama',
          'Özel etkinliklere davet'
        ],
        isPopular: true
      },
      {
        id: 'package3',
        name: 'Yıllık VIP',
        description: '1 yıllık tam erişim ve %25 indirim.',
        price: 450,
        duration: '1 yıl',
        benefits: [
          'Tüm premium içeriklere erişim',
          'Ekstra özel içerikler',
          'Özel mesajlaşma hakkı',
          'Öncelikli cevaplama',
          '1 adet ücretsiz özel istek hakkı',
          'Özel etkinliklere davet'
        ]
      }
    ];
  };
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse text-pink-500 text-xl">Yükleniyor...</div>
      </div>
    );
  }
  
  if (!creator) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-4">
        <div className="text-red-500 text-xl mb-4">Şovcu bulunamadı</div>
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
      {/* Kapak resmi */}
      <div 
        className="h-48 sm:h-64 w-full bg-cover bg-center relative"
        style={{ backgroundImage: `url(${creator.coverImage})` }}
      >
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
        
        {/* Geri butonu */}
        <div className="absolute top-4 left-4">
          <button
            className="bg-black/50 text-white p-2 rounded-full backdrop-blur-sm"
            onClick={() => navigate(-1)}
          >
            ← Geri
          </button>
        </div>
      </div>
      
      {/* Profil Başlığı */}
      <div className="container mx-auto px-4 -mt-16 relative z-10">
        <div className="flex flex-col md:flex-row items-start md:items-end">
          {/* Avatar */}
          <div className="mb-4 md:mb-0 mr-4">
            <div className="relative">
              <img
                src={creator.avatar}
                alt={creator.name}
                className="w-32 h-32 rounded-full border-4 border-pink-500 object-cover"
              />
              
              {/* Online/Offline durumu */}
              {creator.isOnline !== undefined && (
                <div
                  className={`absolute bottom-2 right-2 w-5 h-5 rounded-full border-2 border-black ${
                    creator.isOnline ? 'bg-emerald-500' : 'bg-gray-500'
                  }`}
                />
              )}
              
              {/* Doğrulanmış rozeti */}
              {creator.isVerified && (
                <div className="absolute top-1 right-1 bg-blue-500 text-white p-1 rounded-full w-6 h-6 flex items-center justify-center text-xs">
                  ✓
                </div>
              )}
            </div>
          </div>
          
          {/* Şovcu bilgileri */}
          <div className="flex-1">
            <h1 className="text-3xl font-bold">
              {creator.name} {creator.isVerified && <span className="text-blue-400">✓</span>}
            </h1>
            
            <div className="flex flex-wrap gap-2 mt-2">
              {creator.tags.map((tag, index) => (
                <span
                  key={index}
                  className="bg-white/10 text-white/80 px-2 py-1 rounded-full text-xs"
                >
                  {tag}
                </span>
              ))}
            </div>
            
            <p className="text-gray-300 mt-2 max-w-2xl">{creator.bio}</p>
          </div>
          
          {/* Abonelik butonu */}
          <div className="mt-4 md:mt-0">
            {isSubscribed ? (
              <button
                className="bg-gradient-to-r from-green-500 to-emerald-600 text-white px-6 py-2 rounded-lg font-semibold flex items-center"
                disabled
              >
                <span className="mr-2">✓</span> Abonesiniz
              </button>
            ) : (
              <button
                className="bg-gradient-to-r from-pink-500 to-purple-600 text-white px-6 py-2 rounded-lg font-semibold"
                onClick={() => setActiveTab('packages')}
              >
                Abone Ol
              </button>
            )}
          </div>
        </div>
        
        {/* İstatistikler */}
        <div className="flex justify-between max-w-md mt-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-white">{creator.statistics.contentCount}</div>
            <div className="text-gray-400">İçerik</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-white">{creator.statistics.subscriberCount}</div>
            <div className="text-gray-400">Abone</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-white">{creator.statistics.likes}</div>
            <div className="text-gray-400">Beğeni</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-white">{creator.statistics.views}</div>
            <div className="text-gray-400">Görüntülenme</div>
          </div>
        </div>
        
        {/* Sosyal medya linkleri */}
        {creator.socialLinks && (
          <div className="flex space-x-4 mt-4">
            {creator.socialLinks.instagram && (
              <a
                href={`https://instagram.com/${creator.socialLinks.instagram}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-pink-400 hover:text-pink-300"
              >
                📸 Instagram
              </a>
            )}
            {creator.socialLinks.twitter && (
              <a
                href={`https://twitter.com/${creator.socialLinks.twitter}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-400 hover:text-blue-300"
              >
                🐦 Twitter
              </a>
            )}
            {creator.socialLinks.website && (
              <a
                href={creator.socialLinks.website}
                target="_blank"
                rel="noopener noreferrer"
                className="text-purple-400 hover:text-purple-300"
              >
                🌐 Website
              </a>
            )}
          </div>
        )}
        
        {/* Sekme butonları */}
        <div className="flex border-b border-gray-800 mt-8">
          <button
            className={`py-2 px-4 font-medium ${
              activeTab === 'content'
                ? 'text-pink-500 border-b-2 border-pink-500'
                : 'text-gray-400 hover:text-white'
            }`}
            onClick={() => setActiveTab('content')}
          >
            İçerikler
          </button>
          <button
            className={`py-2 px-4 font-medium ${
              activeTab === 'packages'
                ? 'text-pink-500 border-b-2 border-pink-500'
                : 'text-gray-400 hover:text-white'
            }`}
            onClick={() => setActiveTab('packages')}
          >
            VIP Paketler
          </button>
        </div>
        
        {/* İçerik alanı */}
        <div className="mt-6">
          {activeTab === 'content' && (
            <>
              <h2 className="text-xl font-semibold mb-4">
                {isSubscribed ? 'Tüm İçerikler' : 'İçerikler'}
              </h2>
              
              {contents.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                  {contents.map(content => (
                    <ContentCard
                      key={content.id}
                      id={content.id}
                      title={content.title}
                      thumbnail={content.thumbnail}
                      creatorName={content.creatorName}
                      creatorId={content.creatorId}
                      creatorAvatar={content.creatorAvatar}
                      price={content.price}
                      isPremium={content.isPremium}
                      likes={content.likes}
                      category={content.category}
                      previewText={content.previewText}
                      isSubscribed={isSubscribed}
                      onClick={handleContentClick}
                    />
                  ))}
                </div>
              ) : (
                <div className="text-center py-10 text-gray-400">
                  Henüz içerik paylaşılmamış.
                </div>
              )}
            </>
          )}
          
          {activeTab === 'packages' && (
            <>
              <h2 className="text-xl font-semibold mb-4">VIP Paketler</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {packages.map(packageItem => (
                  <div
                    key={packageItem.id}
                    className={`bg-gradient-to-br ${
                      packageItem.isPopular
                        ? 'from-pink-900/30 to-purple-900/30 border-pink-500/50'
                        : 'from-gray-900/50 to-black/50 border-gray-700/50'
                    } rounded-xl p-6 border relative`}
                  >
                    {packageItem.isPopular && (
                      <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-pink-500 to-purple-600 text-white text-xs py-1 px-3 rounded-full">
                        En Popüler
                      </div>
                    )}
                    
                    <div className="text-xl font-bold mb-1">{packageItem.name}</div>
                    <div className="text-gray-400 text-sm mb-4">{packageItem.description}</div>
                    
                    <div className="flex items-baseline mb-4">
                      <span className="text-3xl font-bold">{packageItem.price}</span>
                      <span className="text-xl ml-1">Star</span>
                      <span className="text-gray-400 ml-2">/ {packageItem.duration}</span>
                    </div>
                    
                    <ul className="mb-6 space-y-2">
                      {packageItem.benefits.map((benefit, index) => (
                        <li key={index} className="flex items-start">
                          <span className="text-emerald-500 mr-2">✓</span>
                          <span>{benefit}</span>
                        </li>
                      ))}
                    </ul>
                    
                    {packageItem.featuredContent && (
                      <div className="mb-4 bg-black/30 rounded-lg overflow-hidden">
                        <img
                          src={packageItem.featuredContent.thumbnail}
                          alt={packageItem.featuredContent.title}
                          className="w-full h-32 object-cover"
                        />
                        <div className="p-2 text-sm">
                          <div className="font-medium">Öne Çıkan İçerik:</div>
                          <div className="text-gray-400">{packageItem.featuredContent.title}</div>
                        </div>
                      </div>
                    )}
                    
                    <button
                      className={`w-full py-2 px-4 rounded-lg font-medium ${
                        isSubscribed
                          ? 'bg-gray-700 text-gray-300 cursor-not-allowed'
                          : 'bg-gradient-to-r from-pink-500 to-purple-600 text-white'
                      }`}
                      onClick={() => !isSubscribed && handleSubscribe(packageItem)}
                      disabled={isSubscribed}
                    >
                      {isSubscribed ? 'Abonesiniz' : 'Abone Ol'}
                    </button>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
      
      {/* Abonelik Modal */}
      {subscribeModalOpen && selectedPackage && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-900 rounded-xl p-6 max-w-md w-full">
            <h3 className="text-xl font-bold mb-4">Abonelik Satın Al</h3>
            <div className="mb-6">
              <div className="flex justify-between mb-2">
                <span>Şovcu:</span>
                <span>{creator.name}</span>
              </div>
              <div className="flex justify-between mb-2">
                <span>Paket:</span>
                <span>{selectedPackage.name}</span>
              </div>
              <div className="flex justify-between mb-2">
                <span>Süre:</span>
                <span>{selectedPackage.duration}</span>
              </div>
              <div className="flex justify-between mb-2">
                <span>Fiyat:</span>
                <span>{selectedPackage.price} Star</span>
              </div>
              <div className="flex justify-between mb-4">
                <span>Mevcut Bakiye:</span>
                <span className={userBalance < selectedPackage.price ? 'text-red-500' : 'text-emerald-500'}>
                  {userBalance} Star
                </span>
              </div>
              
              {userBalance < selectedPackage.price && (
                <div className="bg-red-900/50 text-red-300 p-3 rounded-lg mb-4">
                  Yetersiz bakiye. Daha fazla Star satın almanız gerekiyor.
                </div>
              )}
            </div>
            
            <div className="flex justify-end space-x-2">
              <button
                className="px-4 py-2 bg-gray-700 text-white rounded-lg"
                onClick={() => setSubscribeModalOpen(false)}
              >
                İptal
              </button>
              <button
                className="px-4 py-2 bg-gradient-to-r from-pink-500 to-purple-600 text-white rounded-lg"
                onClick={handleSubscribeConfirm}
                disabled={userBalance < selectedPackage.price}
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

export default CreatorProfile; 