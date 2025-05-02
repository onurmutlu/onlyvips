import { api } from './api';

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  createdAt: Date;
  readAt?: Date;
}

export interface CreateNotificationData {
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
}

export const notificationService = {
  getAll: async (): Promise<Notification[]> => {
    const { data } = await api.get('/api/notifications');
    return data;
  },

  getUnread: async (): Promise<Notification[]> => {
    const { data } = await api.get('/api/notifications/unread');
    return data;
  },

  getById: async (id: string): Promise<Notification> => {
    const { data } = await api.get(`/api/notifications/${id}`);
    return data;
  },

  create: async (data: CreateNotificationData): Promise<Notification> => {
    const { data: createdNotification } = await api.post('/api/notifications', data);
    return createdNotification;
  },

  markAsRead: async (id: string): Promise<void> => {
    await api.put(`/api/notifications/${id}/read`);
  },

  markAllAsRead: async (): Promise<void> => {
    await api.put('/api/notifications/read-all');
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/notifications/${id}`);
  },

  deleteAll: async (): Promise<void> => {
    await api.delete('/api/notifications');
  }
}; 