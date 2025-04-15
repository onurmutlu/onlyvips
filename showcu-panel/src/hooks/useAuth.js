import { useState, useEffect } from 'react';
import { useTelegramContext } from '../TelegramProvider';
import axios from 'axios';

export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isShowcu, setIsShowcu] = useState(false);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { user, isReady } = useTelegramContext();

  // Telegram kullanıcı bilgisi ile kimlik doğrulama
  useEffect(() => {
    const authenticate = async () => {
      if (!isReady || !user) {
        setLoading(false);
        return;
      }

      try {
        // Kullanıcı verileri ile kimlik doğrulama isteği
        const response = await axios.post(`${import.meta.env.VITE_API_URL}/auth/telegram`, {
          telegram_id: user.id,
          username: user.username,
          first_name: user.first_name,
          last_name: user.last_name,
        });

        // JWT token'ı kaydet
        const { token, user: userData } = response.data;
        localStorage.setItem('token', token);
        setToken(token);
        setIsAuthenticated(true);
        setIsShowcu(userData.role === 'showcu');
        setError(null);
      } catch (err) {
        console.error('Kimlik doğrulama hatası:', err);
        setError('Giriş yapılamadı. Lütfen daha sonra tekrar deneyin.');
        setIsAuthenticated(false);
        setIsShowcu(false);
        localStorage.removeItem('token');
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      // Mevcut token varsa doğrula
      verifyToken();
    } else if (isReady) {
      // Token yoksa ve Telegram hazırsa yeni giriş yap
      authenticate();
    }
  }, [isReady, user]);

  // Token doğrulama
  const verifyToken = async () => {
    if (!token) {
      setIsAuthenticated(false);
      setLoading(false);
      return;
    }

    try {
      const response = await axios.get(`${import.meta.env.VITE_API_URL}/auth/verify`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setIsAuthenticated(true);
      setIsShowcu(response.data.user.role === 'showcu');
      setError(null);
    } catch (err) {
      console.error('Token doğrulama hatası:', err);
      setIsAuthenticated(false);
      setIsShowcu(false);
      localStorage.removeItem('token');
      setError('Oturumunuz sona erdi. Lütfen tekrar giriş yapın.');
    } finally {
      setLoading(false);
    }
  };

  // Çıkış yapma
  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setIsAuthenticated(false);
    setIsShowcu(false);
  };

  return {
    isAuthenticated,
    isShowcu,
    token,
    loading,
    error,
    logout,
  };
}; 