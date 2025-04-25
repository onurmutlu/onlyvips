import { create } from 'zustand';
import { authService } from '../services';

interface AuthState {
  isAuthenticated: boolean;
  user: {
    id: string;
    username: string;
    email: string;
    telegramId: string;
    role: 'admin' | 'creator' | 'user';
  } | null;
  login: (email: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string, telegramId: string) => Promise<void>;
  logout: () => Promise<void>;
}

export const useAuth = create<AuthState>((set) => ({
  isAuthenticated: !!localStorage.getItem('token'),
  user: null,
  login: async (email: string, password: string) => {
    const response = await authService.login({ email, password });
    localStorage.setItem('token', response.token);
    set({ isAuthenticated: true, user: response.user });
  },
  register: async (username: string, email: string, password: string, telegramId: string) => {
    const response = await authService.register({ username, email, password, telegramId });
    localStorage.setItem('token', response.token);
    set({ isAuthenticated: true, user: response.user });
  },
  logout: async () => {
    await authService.logout();
    localStorage.removeItem('token');
    set({ isAuthenticated: false, user: null });
  }
})); 