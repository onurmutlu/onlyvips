import api from './api';

interface Package {
  id: string;
  name: string;
  description: string;
  price: number;
  duration: number; // days
  features: string[];
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

interface CreatePackageData {
  name: string;
  description: string;
  price: number;
  duration: number;
  features: string[];
}

export const packageService = {
  async getAll() {
    const response = await api.get<Package[]>('/packages');
    return response.data;
  },

  async getById(id: string) {
    const response = await api.get<Package>(`/packages/${id}`);
    return response.data;
  },

  async create(data: CreatePackageData) {
    const response = await api.post<Package>('/packages', data);
    return response.data;
  },

  async update(id: string, data: Partial<CreatePackageData>) {
    const response = await api.put<Package>(`/packages/${id}`, data);
    return response.data;
  },

  async delete(id: string) {
    await api.delete(`/packages/${id}`);
  },

  async getSubscribers(id: string) {
    const response = await api.get(`/packages/${id}/subscribers`);
    return response.data;
  },

  async getAnalytics(id: string) {
    const response = await api.get(`/packages/${id}/analytics`);
    return response.data;
  }
}; 