/**
 * OnlyVips - MiniApp API Client
 * 
 * İçerik şovcuları, kullanıcı profilleri ve ödeme işlemleri için API erişim noktaları
 */

// API temel URL'i
const API_BASE_URL = 'https://api.onlyvips.com';

// Temel API çağrıları için yardımcı fonksiyon
const apiCall = async (endpoint: string, method: string = 'GET', data: any = null) => {
  try {
    const options: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      credentials: 'include'  // Çerez (Cookie) bazlı kimlik doğrulama için
    };

    // Telegram webApp verileri
    const telegramData = window.Telegram?.WebApp?.initDataUnsafe;
    if (telegramData) {
      options.headers = {
        ...options.headers,
        'X-Telegram-Init-Data': JSON.stringify(telegramData)
      };
    }

    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
      options.body = JSON.stringify(data);
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
    
    // Hata durumunu kontrol et
    if (!response.ok) {
      const errorData = await response.json();
      return {
        success: false,
        status: response.status,
        error: errorData.message || 'Bir hata oluştu',
        data: null
      };
    }
    
    const responseData = await response.json();

    return {
      success: response.ok,
      status: response.status,
      data: responseData
    };
  } catch (error) {
    console.error(`API İsteği Hatası (${endpoint}):`, error);
    
    return {
      success: false,
      status: 0,
      error: 'Bağlantı hatası',
      data: null
    };
  }
};

// API istemcisi
const api = {
  // İçerik İşlemleri
  content: {
    // Kategorileri getir
    getCategories: () => apiCall('/content/categories'),
    
    // Öne çıkan içerikleri getir
    getFeatured: (userId: string) => apiCall(`/content/featured?userId=${userId}`),
    
    // En son eklenen içerikleri getir
    getLatest: (userId: string) => apiCall(`/content/latest?userId=${userId}`),
    
    // İçerik detaylarını getir
    getDetails: (contentId: string, userId: string) => 
      apiCall(`/content/${contentId}?userId=${userId}`),
    
    // İçeriği beğen
    like: (contentId: string, userId: string) => 
      apiCall(`/content/${contentId}/like`, 'POST', { userId }),
    
    // İçeriğe yorum ekle
    addComment: (contentId: string, userId: string, comment: string) => 
      apiCall(`/content/${contentId}/comment`, 'POST', { userId, comment }),
    
    // İçerik ara
    search: (query: string, userId: string) => 
      apiCall(`/content/search?q=${encodeURIComponent(query)}&userId=${userId}`),
    
    // Kategoriye göre filtrele
    filterByCategory: (categoryId: string, userId: string) => 
      apiCall(`/content/filter?category=${encodeURIComponent(categoryId)}&userId=${userId}`)
  },
  
  // Şovcu İşlemleri
  creators: {
    // Tüm şovcuları getir
    getAll: () => apiCall('/creators'),
    
    // Popüler şovcuları getir
    getPopular: () => apiCall('/creators/popular'),
    
    // Şovcu profilini getir
    getProfile: (creatorId: string, userId: string) => 
      apiCall(`/creators/${creatorId}?userId=${userId}`),
    
    // Şovcu içeriklerini getir
    getContent: (creatorId: string, userId: string) => 
      apiCall(`/creators/${creatorId}/content?userId=${userId}`),
    
    // Şovcuya abone ol
    subscribe: (creatorId: string, userId: string, packageId: string) => 
      apiCall(`/creators/${creatorId}/subscribe`, 'POST', { userId, packageId }),
    
    // Şovcu ara
    search: (query: string) => 
      apiCall(`/creators/search?q=${encodeURIComponent(query)}`)
  },
  
  // Kullanıcı İşlemleri
  user: {
    // Kullanıcı profilini getir
    getProfile: (userId: string) => apiCall(`/users/${userId}`),
    
    // Kullanıcı cüzdanını getir
    getWallet: (userId: string) => apiCall(`/users/${userId}/wallet`),
    
    // Favori içerikleri getir
    getFavorites: (userId: string) => apiCall(`/users/${userId}/favorites`),
    
    // İçeriği favorilere ekle
    addFavorite: (userId: string, contentId: string) => 
      apiCall(`/users/${userId}/favorites`, 'POST', { contentId }),
    
    // Abonelikleri getir
    getSubscriptions: (userId: string) => apiCall(`/users/${userId}/subscriptions`),
    
    // Kullanıcı adını güncelle 
    updateUsername: (userId: string, username: string) => 
      apiCall(`/users/${userId}/profile`, 'PATCH', { username })
  },
  
  // Paket İşlemleri
  packages: {
    // Tüm paketleri getir
    getAll: () => apiCall('/packages'),
    
    // Şovcuya ait paketleri getir
    getByCreator: (creatorId: string) => apiCall(`/packages/creator/${creatorId}`),
    
    // Paket satın al
    purchase: (packageId: string, userId: string, paymentMethod: string) => 
      apiCall('/packages/purchase', 'POST', { packageId, userId, paymentMethod }),
    
    // Paket detaylarını getir
    getDetails: (packageId: string) => apiCall(`/packages/${packageId}`)
  },
  
  // Ödeme İşlemleri
  payments: {
    // Star satın al
    purchaseStars: (userId: string, amount: number, paymentMethod: string) => 
      apiCall('/payments/stars', 'POST', { userId, amount, paymentMethod }),
    
    // İşlem geçmişini getir
    getHistory: (userId: string) => apiCall(`/payments/history/${userId}`),
    
    // Ödeme yöntemlerini getir
    getMethods: () => apiCall('/payments/methods'),
    
    // Ton Pay ile ödeme başlat
    initiateTonPay: (userId: string, amount: number) => 
      apiCall('/payments/ton/initiate', 'POST', { userId, amount }),
    
    // Ödeme durumunu kontrol et
    checkStatus: (paymentId: string) => apiCall(`/payments/status/${paymentId}`)
  }
};

export default api;