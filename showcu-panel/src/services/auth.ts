import { api } from './api';

export interface AuthResponse {
  token: string;
  user: {
    id: string;
    username: string;
    email: string;
    role: 'admin' | 'creator' | 'user';
  };
}

export interface LoginData {
  email: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  role: 'creator' | 'user';
}

export const authService = {
  login: async (data: LoginData): Promise<AuthResponse> => {
    const { data: response } = await api.post('/api/auth/login', data);
    return response;
  },

  register: async (data: RegisterData): Promise<AuthResponse> => {
    const { data: response } = await api.post('/api/auth/register', data);
    return response;
  },

  logout: async (): Promise<void> => {
    await api.post('/api/auth/logout');
  },

  refreshToken: async (): Promise<AuthResponse> => {
    const { data: response } = await api.post('/api/auth/refresh');
    return response;
  },

  forgotPassword: async (email: string): Promise<void> => {
    await api.post('/api/auth/forgot-password', { email });
  },

  resetPassword: async (token: string, password: string): Promise<void> => {
    await api.post('/api/auth/reset-password', { token, password });
  },

  getCurrentUser: async (): Promise<AuthResponse['user']> => {
    const { data } = await api.get('/api/auth/me');
    return data;
  },

  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  },

  verifyEmail: async (token: string): Promise<void> => {
    await api.post('/auth/verify-email', { token });
  }
}; 