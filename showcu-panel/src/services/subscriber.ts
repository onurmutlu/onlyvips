import { api } from './api';

export interface Subscriber {
  id: string;
  userId: string;
  packageId: string;
  status: 'active' | 'expired' | 'cancelled';
  startDate: Date;
  endDate: Date;
  createdAt: Date;
  updatedAt: Date;
}

export const subscriberService = {
  getAll: async (): Promise<Subscriber[]> => {
    const { data } = await api.get('/api/subscribers');
    return data;
  },

  getById: async (id: string): Promise<Subscriber> => {
    const { data } = await api.get(`/api/subscribers/${id}`);
    return data;
  },

  getByUserId: async (userId: string): Promise<Subscriber[]> => {
    const { data } = await api.get(`/api/subscribers/user/${userId}`);
    return data;
  },

  getByPackageId: async (packageId: string): Promise<Subscriber[]> => {
    const { data } = await api.get(`/api/subscribers/package/${packageId}`);
    return data;
  },

  create: async (userId: string, packageId: string): Promise<Subscriber> => {
    const { data } = await api.post('/api/subscribers', { userId, packageId });
    return data;
  },

  cancel: async (id: string): Promise<Subscriber> => {
    const { data } = await api.put(`/api/subscribers/${id}/cancel`);
    return data;
  },

  getAnalytics: async (): Promise<any> => {
    const { data } = await api.get('/api/subscribers/analytics');
    return data;
  }
}; 