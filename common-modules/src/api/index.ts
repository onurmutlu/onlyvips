import axios, { AxiosRequestConfig } from 'axios';

// API URL'sini ortam değişkeninden al
const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000';

// Axios instance oluştur
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// İstek interceptor'ü ekle
api.interceptors.request.use((config) => {
  // LocalStorage'dan JWT token'ı al
  const token = localStorage.getItem('auth_token');
  
  // Token varsa, Authorization header'ına ekle
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  return config;
});

// Response interceptor'ü ekle
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // 401 Unauthorized hatası alındığında oturumu sonlandır
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('auth_token');
      // Burada oturum sonlandırma işlemleri yapılabilir
    }
    
    return Promise.reject(error);
  }
);

export default api;

// API endpoint fonksiyonları buraya eklenebilir
export * from './auth';
export * from './content';
export * from './packages'; 