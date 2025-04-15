import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// İstek interceptor'ı için token ekleme
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Hata işleme interceptor'ı
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // 401 Unauthorized hatası durumunda oturumu sonlandır
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      // Telegram MiniApp'se ana uygulamaya yönlendir
      if (window.Telegram?.WebApp) {
        window.Telegram.WebApp.close();
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient; 