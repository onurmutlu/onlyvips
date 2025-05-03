import api from './index';
import { User } from '../types';

export interface TelegramAuthParams {
  telegramId: string;
  username?: string;
  firstName?: string;
  lastName?: string;
  photoUrl?: string;
}

export interface AuthResponse {
  token: string;
  user: User;
}

// Telegram ile giriş/kayıt
export const telegramAuth = async (params: TelegramAuthParams): Promise<AuthResponse> => {
  const response = await api.post<AuthResponse>('/api/auth/telegram', params);
  return response.data;
};

// Kullanıcı bilgilerini getir
export const getCurrentUser = async (): Promise<User> => {
  const response = await api.get<{ user: User }>('/api/auth/me');
  return response.data.user;
}; 