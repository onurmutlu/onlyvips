/**
 * OnlyVips - Showcu Panel API Client
 */

// API temel URL'i
const API_BASE_URL = 'https://api.onlyvips.com';

// API çağrıları için yardımcı fonksiyon
const apiCall = async (endpoint: string, method: string = 'GET', data: any = null) => {
  try {
    const token = localStorage.getItem('creator_token');
    
    const options: RequestInit = {
      method,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/json'
      }
    };

    if (data) {
      if (data instanceof FormData) {
        options.body = data;
      } else if (method === 'POST' || method === 'PUT' || method === 'PATCH') {
        options.headers = {
          ...options.headers,
          'Content-Type': 'application/json'
        };
        options.body = JSON.stringify(data);
      }
    }

    const response = await fetch(`${API_BASE_URL}/creator-panel${endpoint}`, options);
    
    // Token süresi dolmuşsa
    if (response.status === 401) {
      localStorage.removeItem('creator_token');
      window.location.href = '/login';
      return {
        success: false,
        error: 'Oturum süresi doldu, lütfen tekrar giriş yapın',
        data: null
      };
    }
    
    // Hata durumunu kontrol et
    if (!response.ok) {
      const errorData = await response.json();
      return {
        success: false,
        error: errorData.message || 'Bir hata oluştu',
        data: null
      };
    }
    
    const responseData = await response.json();

    return {
      success: true,
      data: responseData.data
    };
  } catch (error) {
    console.error(`API İsteği Hatası (${endpoint}):`, error);
    
    return {
      success: false,
      error: 'Bağlantı hatası',
      data: null
    };
  }
};

// Şovcu panel API istemcisi
const api = {
  // Kimlik doğrulama
  login: (username: string, password: string) => 
    apiCall('/login', 'POST', { username, password }),
  
  // İçerik yönetimi
  getCreatorContent: () => apiCall('/content'),
  
  createContent: (formData: FormData) => 
    apiCall('/content', 'POST', formData),
  
  updateContent: (contentId: string, formData: FormData) => 
    apiCall(`/content/${contentId}`, 'PUT', formData),
  
  deleteContent: (contentId: string) => 
    apiCall(`/content/${contentId}`, 'DELETE'),
  
  // Paket yönetimi
  getCreatorPackages: () => apiCall('/packages'),
  
  createPackage: (packageData: any) => 
    apiCall('/packages', 'POST', packageData),
  
  updatePackage: (packageId: string, packageData: any) => 
    apiCall(`/packages/${packageId}`, 'PUT', packageData),
  
  deletePackage: (packageId: string) => 
    apiCall(`/packages/${packageId}`, 'DELETE'),
  
  // İstatistikler
  getStatistics: (period: 'week' | 'month' | 'year' = 'month') => 
    apiCall(`/statistics?period=${period}`),
  
  // Aboneler
  getSubscribers: () => apiCall('/subscribers'),
  
  // Kazançlar
  getEarnings: (period: 'week' | 'month' | 'year' = 'month') => 
    apiCall(`/earnings?period=${period}`),
  
  // Ödemeler
  initiateWithdrawal: (amount: number, walletAddress: string) => 
    apiCall('/payments/withdraw', 'POST', { amount, walletAddress }),
  
  getWithdrawalHistory: () => apiCall('/payments/withdrawals')
};

export default api;
