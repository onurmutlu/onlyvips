import api from './api';

interface LoginData {
  email: string;
  password: string;
}

interface RegisterData {
  username: string;
  email: string;
  password: string;
  telegramId: string;
}

interface AuthResponse {
  token: string;
  user: {
    id: string;
    username: string;
    email: string;
    telegramId: string;
    role: 'admin' | 'creator' | 'user';
  };
}

export const authService = {
  async login(data: LoginData) {
    const response = await api.post<AuthResponse>('/auth/login', data);
    return response.data;
  },

  async register(data: RegisterData) {
    const response = await api.post<AuthResponse>('/auth/register', data);
    return response.data;
  },

  async logout() {
    await api.post('/auth/logout');
  },

  async refreshToken() {
    const response = await api.post<AuthResponse>('/auth/refresh');
    return response.data;
  },

  async forgotPassword(email: string) {
    await api.post('/auth/forgot-password', { email });
  },

  async resetPassword(token: string, password: string) {
    await api.post('/auth/reset-password', { token, password });
  },

  async verifyEmail(token: string) {
    await api.post('/auth/verify-email', { token });
  }
}; 