import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/apiClient';
import ContentCard from '../components/ContentCard';
import CreatorCard from '../components/CreatorCard';

interface Category {
  id: string;
  name: string;
  icon: string;
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

interface Creator {
  id: string;
  name: string;
  avatar: string;
  coverImage: string;
  bio: string;
  statistics: {
    contentCount: number;
    subscriberCount: number;
    likes: number;
  };
  tags: string[];
  featuredPackage?: {
    id: string;
    name: string;
    price: number;
  };
  isVerified: boolean;
  isOnline: boolean;
}

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState('all');
  const [categories, setCategories] = useState<Category[]>([]);
  const [featuredContent, setFeaturedContent] = useState<Content[]>([]);
  const [latestContent, setLatestContent] = useState<Content[]>([]);
  const [popularCreators, setPopularCreators] = useState<Creator[]>([]);
  const [userSubscriptions, setUserSubscriptions] = useState<string[]>([]);
  
  // Kullanıcı ID'sini al (gerçekte Telegram WebApp'ten alınacak)
  const userId = window.Telegram?.WebApp?.initDataUnsafe?.user?.id || 'demo-user';
  
  useEffect(() => {
    // miniapp/src/pages/Home.tsx içinde loadData fonksiyonu
    const loadData = async () => {
      try {
        setLoading(true);
        
        // Kategorileri yükle
        const categoriesResponse = await api.content.getCategories();
        if (categoriesResponse.success) {
          setCategories(categoriesResponse.data.categories);
        }
        
        // Öne çıkan içerikleri yükle
        const featuredResponse = await api.content.getFeatured(userId);
        if (featuredResponse.success) {
          setFeaturedContent(featuredResponse.data.content);
        } else {
          // API çağrısı başarısız olursa mock veri kullan
          setFeaturedContent(getMockFeaturedContent());
        }
        
        // En son eklenen içerikleri yükle
        const latestResponse = await api.content.getLatest(userId);
        if (latestResponse.success) {
          setLatestContent(latestResponse.data.content);
        } else {
          setLatestContent(getMockLatestContent());
        }
        
        // Popüler şovcuları yükle
        const creatorsResponse = await api.creators.getPopular();
        if (creatorsResponse.success) {
          setPopularCreators(creatorsResponse.data.creators);
        } else {
          setPopularCreators(getMockCreators());
        }
        
        // Kullanıcı cüzdanını yükle
        const walletResponse = await api.user.getWallet(userId);
        if (walletResponse.success) {
          setUserBalance(walletResponse.data.balance);
        }
        
      } catch (error) {
        console.error("Veri yükleme hatası:", error);
        // Hata durumunda mock verileri kullan
        setFeaturedContent(getMockFeaturedContent());
        setLatestContent(getMockLatestContent());
        setPopularCreators(getMockCreators());
      } finally {
        setLoading(false);
      }
    };
    
    loadData();
  }, [userId]);
  
  const handleCategoryChange = (categoryId: string) => {
    setActiveCategory(categoryId);
    // Gerçek uygulamada bu kategoriye göre içeriği filtreleyecek
  };
  
  const handleContentClick = (contentId: string) => {
    navigate(`/content/${contentId}`);
  };
  
  // Demo için mock veriler
  const getMockFeaturedContent = (): Content[] => {
    return [
      {
        id: 'content1',
        title: 'Moda Çekimi - Yaz Koleksiyonu',
        thumbnail: 'https://picsum.photos/id/91/600/400',
        creatorName: 'Aylin Sezer',
        creatorId: 'creator1',
        creatorAvatar: 'https://i.pravatar.cc/150?img=29',
        price: 15,
        isPremium: true,
        likes: 124,
        category: 'photo',
        previewText: 'Yeni yaz koleksiyonum ile çok özel pozlar...'
      },
      {
        id: 'content2',
        title: 'Jakuzi Özel Video',
        thumbnail: 'https://picsum.photos/id/342/600/400',
        creatorName: 'Deniz Yıldız',
        creatorId: 'creator2',
        creatorAvatar: 'https://i.pravatar.cc/150?img=16',
        price: 30,
        isPremium: true,
        likes: 218,
        category: 'video',
        previewText: 'Su altı kamera ile özel çekim...'
      },
      {
        id: 'content3',
        title: 'Gece Sohbeti - ASMR',
        thumbnail: 'https://picsum.photos/id/193/600/400',
        creatorName: 'Selin Aydın',
        creatorId: 'creator3',
        creatorAvatar: 'https://i.pravatar.cc/150?img=23',
        isPremium: false,
        likes: 97,
        category: 'audio'
      }
    ];
  };
  
  const getMockLatestContent = (): Content[] => {
    return [
      {
        id: 'content4',
        title: 'Plaj Günlüğü',
        thumbnail: 'https://picsum.photos/id/152/600/400',
        creatorName: 'Ebru Koç',
        creatorId: 'creator4',
        creatorAvatar: 'https://i.pravatar.cc/150?img=5',
        isPremium: false,
        likes: 64,
        category: 'photo'
      },
      {
        id: 'content5',
        title: 'Ayışığında Fısıltılar',
        thumbnail: 'https://picsum.photos/id/167/600/400',
        creatorName: 'Zeynep Demir',
        creatorId: 'creator5',
        creatorAvatar: 'https://i.pravatar.cc/150?img=9',
        price: 10,
        isPremium: true,
        likes: 89,
        category: 'audio',
        previewText: 'Hassas mikrofonla kaydedilmiş fısıltılar...'
      }
    ];
  };
  
  const getMockCreators = (): Creator[] => {
    return [
      {
        id: 'creator1',
        name: 'Aylin Sezer',
        avatar: 'https://i.pravatar.cc/150?img=29',
        coverImage: 'https://picsum.photos/id/22/600/200',
        bio: 'Model ve fotoğraf sanatçısı. Özel çekimler ve koleksiyonlar paylaşıyorum.',
        statistics: {
          contentCount: 42,
          subscriberCount: 1250,
          likes: 7845
        },
        tags: ['model', 'fotoğraf', 'moda'],
        featuredPackage: {
          id: 'package1',
          name: 'VIP Aylık',
          price: 100
        },
        isVerified: true,
        isOnline: true
      },
      {
        id: 'creator2',
        name: 'Deniz Yıldız',
        avatar: 'https://i.pravatar.cc/150?img=16',
        coverImage: 'https://picsum.photos/id/326/600/200',
        bio: 'Yüzücü ve fitness tutkunu. Su altı ve havuz videoları.',
        statistics: {
          contentCount: 28,
          subscriberCount: 975,
          likes: 5263
        },
        tags: ['fitness', 'yüzme', 'video'],
        featuredPackage: {
          id: 'package2',
          name: 'Premium',
          price: 75
        },
        isVerified: true,
        isOnline: false
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
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-gray-800 text-white pb-20">
      {/* Hero Banner */}
      <div className="bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 p-6 text-white">
        <h1 className="text-2xl font-bold">OnlyVips</h1>
        <p className="text-white/80">Özel içerikler ve VIP deneyim</p>
      </div>
      
      {/* Kategori Seçimi */}
      <div className="px-4 py-4 overflow-x-auto">
        <div className="flex space-x-2">
          <button
            className={`px-4 py-2 rounded-full text-sm whitespace-nowrap ${
              activeCategory === 'all'
                ? 'bg-gradient-to-r from-pink-500 to-indigo-500 text-white'
                : 'bg-white/10 text-white/80'
            }`}
            onClick={() => handleCategoryChange('all')}
          >
            🔥 Tümü
          </button>
          
          {categories.map(category => (
            <button
              key={category.id}
              className={`px-4 py-2 rounded-full text-sm whitespace-nowrap ${
                activeCategory === category.id
                  ? 'bg-gradient-to-r from-pink-500 to-indigo-500 text-white'
                  : 'bg-white/10 text-white/80'
              }`}
              onClick={() => handleCategoryChange(category.id)}
            >
              {category.icon} {category.name}
            </button>
          ))}
        </div>
      </div>
      
      {/* Öne Çıkan İçerikler */}
      <section className="px-4 py-6">
        <h2 className="text-xl font-semibold mb-4">✨ Öne Çıkan İçerikler</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {featuredContent.map(content => (
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
              isSubscribed={userSubscriptions.includes(content.creatorId)}
              onClick={handleContentClick}
            />
          ))}
        </div>
      </section>
      
      {/* Popüler Şovcular */}
      <section className="px-4 py-6">
        <h2 className="text-xl font-semibold mb-4">🌟 Popüler Şovcular</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {popularCreators.map(creator => (
            <CreatorCard
              key={creator.id}
              id={creator.id}
              name={creator.name}
              avatar={creator.avatar}
              coverImage={creator.coverImage}
              bio={creator.bio}
              statistics={creator.statistics}
              tags={creator.tags}
              featuredPackage={creator.featuredPackage}
              isVerified={creator.isVerified}
              isOnline={creator.isOnline}
            />
          ))}
        </div>
      </section>
      
      {/* En Son Eklenen İçerikler */}
      <section className="px-4 py-6">
        <h2 className="text-xl font-semibold mb-4">🆕 Yeni Eklenenler</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {latestContent.map(content => (
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
              isSubscribed={userSubscriptions.includes(content.creatorId)}
              onClick={handleContentClick}
            />
          ))}
        </div>
      </section>
    </div>
  );
};

export default Home; 