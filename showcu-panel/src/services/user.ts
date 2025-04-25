import api from './api';

interface User {
  id: string;
  username: string;
  email: string;
  telegramId: string;
  role: 'admin' | 'creator' | 'user';
  status: 'active' | 'inactive' | 'banned';
  createdAt: string;
  updatedAt: string;
}

interface CreateUserData {
  username: string;
  email: string;
  telegramId: string;
  role: 'admin' | 'creator' | 'user';
}

export const userService = {
  async getAll() {
    const response = await api.get<User[]>('/users');
    return response.data;
  },

  async getById(id: string) {
    const response = await api.get<User>(`/users/${id}`);
    return response.data;
  },

  async create(data: CreateUserData) {
    const response = await api.post<User>('/users', data);
    return response.data;
  },

  async update(id: string, data: Partial<CreateUserData>) {
    const response = await api.put<User>(`/users/${id}`, data);
    return response.data;
  },

  async delete(id: string) {
    await api.delete(`/users/${id}`);
  },

  async getByTelegramId(telegramId: string) {
    const response = await api.get<User>(`/users/telegram/${telegramId}`);
    return response.data;
  },

  async getAnalytics() {
    const response = await api.get('/users/analytics');
    return response.data;
  }
}; 