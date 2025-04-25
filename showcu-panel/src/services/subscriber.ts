import api from './api';

interface Subscriber {
  id: string;
  userId: string;
  username: string;
  packageId: string;
  packageName: string;
  startDate: string;
  endDate: string;
  status: 'active' | 'expired' | 'cancelled';
  createdAt: string;
  updatedAt: string;
}

interface CreateSubscriberData {
  userId: string;
  packageId: string;
}

export const subscriberService = {
  async getAll() {
    const response = await api.get<Subscriber[]>('/subscribers');
    return response.data;
  },

  async getById(id: string) {
    const response = await api.get<Subscriber>(`/subscribers/${id}`);
    return response.data;
  },

  async create(data: CreateSubscriberData) {
    const response = await api.post<Subscriber>('/subscribers', data);
    return response.data;
  },

  async update(id: string, data: Partial<CreateSubscriberData>) {
    const response = await api.put<Subscriber>(`/subscribers/${id}`, data);
    return response.data;
  },

  async delete(id: string) {
    await api.delete(`/subscribers/${id}`);
  },

  async getByPackageId(packageId: string) {
    const response = await api.get(`/subscribers/package/${packageId}`);
    return response.data;
  },

  async getAnalytics() {
    const response = await api.get('/subscribers/analytics');
    return response.data;
  }
}; 