import api from './api';

interface Notification {
  id: string;
  userId: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  read: boolean;
  createdAt: string;
}

interface CreateNotificationData {
  userId: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
}

export const notificationService = {
  async getAll() {
    const response = await api.get<Notification[]>('/notifications');
    return response.data;
  },

  async getUnread() {
    const response = await api.get<Notification[]>('/notifications/unread');
    return response.data;
  },

  async getById(id: string) {
    const response = await api.get<Notification>(`/notifications/${id}`);
    return response.data;
  },

  async create(data: CreateNotificationData) {
    const response = await api.post<Notification>('/notifications', data);
    return response.data;
  },

  async markAsRead(id: string) {
    const response = await api.put<Notification>(`/notifications/${id}/read`);
    return response.data;
  },

  async markAllAsRead() {
    const response = await api.put<Notification[]>('/notifications/read-all');
    return response.data;
  },

  async delete(id: string) {
    await api.delete(`/notifications/${id}`);
  },

  async deleteAll() {
    await api.delete('/notifications');
  }
}; 