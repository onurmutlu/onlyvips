import { api } from './api';

export interface User {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'creator' | 'user';
  status: 'active' | 'inactive' | 'banned';
  createdAt: Date;
  updatedAt: Date;
}

export interface UpdateUserData {
  username?: string;
  email?: string;
  role?: 'admin' | 'creator' | 'user';
  status?: 'active' | 'inactive' | 'banned';
}

export const userService = {
  getAll: async (): Promise<User[]> => {
    const { data } = await api.get('/api/users');
    return data;
  },

  getById: async (id: string): Promise<User> => {
    const { data } = await api.get(`/api/users/${id}`);
    return data;
  },

  getByUsername: async (username: string): Promise<User> => {
    const { data } = await api.get(`/api/users/username/${username}`);
    return data;
  },

  update: async (id: string, data: UpdateUserData): Promise<User> => {
    const { data: updatedUser } = await api.put(`/api/users/${id}`, data);
    return updatedUser;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/users/${id}`);
  },

  getAnalytics: async (): Promise<any> => {
    const { data } = await api.get('/api/users/analytics');
    return data;
  }
}; 