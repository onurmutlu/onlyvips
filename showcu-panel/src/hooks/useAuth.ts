import { useState, useCallback, useEffect } from 'react';

interface User {
  id: string;
  username: string;
  email: string;
  name: string;
}

interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
}

const DEMO_USER: User = {
  id: '1',
  username: 'demo',
  email: 'demo@onlyvips.com',
  name: 'Demo Kullanıcı'
};

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>(() => {
    // LocalStorage'dan auth durumunu kontrol et
    const storedAuth = localStorage.getItem('auth');
    return storedAuth ? JSON.parse(storedAuth) : {
      isAuthenticated: false,
      user: null
    };
  });

  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'auth') {
        const newAuth = e.newValue ? JSON.parse(e.newValue) : {
          isAuthenticated: false,
          user: null
        };
        setAuthState(newAuth);
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    return new Promise<boolean>((resolve) => {
      setTimeout(() => {
        // Demo giriş bilgileri
        if (username === 'demo' && password === 'demo123') {
          const newAuthState = {
            isAuthenticated: true,
            user: DEMO_USER
          };
          setAuthState(newAuthState);
          // LocalStorage'a kaydet
          localStorage.setItem('auth', JSON.stringify(newAuthState));
          resolve(true);
        } else {
          resolve(false);
        }
      }, 500);
    });
  }, []);

  const logout = useCallback(() => {
    const newAuthState = {
      isAuthenticated: false,
      user: null
    };
    setAuthState(newAuthState);
    // LocalStorage'dan sil
    localStorage.removeItem('auth');
  }, []);

  return {
    isAuthenticated: authState.isAuthenticated,
    user: authState.user,
    login,
    logout
  };
}; 