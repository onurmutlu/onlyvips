import { api } from './api';

export interface Package {
  id: string;
  name: string;
  description: string;
  price: number;
  duration: number; // days
  features: string[];
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface CreatePackageData {
  name: string;
  description: string;
  price: number;
  duration: number;
  features: string[];
}

export const packageService = {
  getAll: async (): Promise<Package[]> => {
    const { data } = await api.get('/api/packages');
    return data;
  },

  getById: async (id: string): Promise<Package> => {
    const { data } = await api.get(`/api/packages/${id}`);
    return data;
  },

  create: async (data: CreatePackageData): Promise<Package> => {
    const { data: createdPackage } = await api.post('/api/packages', data);
    return createdPackage;
  },

  update: async (id: string, data: Partial<CreatePackageData>): Promise<Package> => {
    const { data: updatedPackage } = await api.put(`/api/packages/${id}`, data);
    return updatedPackage;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/packages/${id}`);
  },

  toggleStatus: async (id: string): Promise<Package> => {
    const { data } = await api.put(`/api/packages/${id}/toggle-status`);
    return data;
  },

  getSubscribers: async (id: string): Promise<any[]> => {
    const { data } = await api.get(`/api/packages/${id}/subscribers`);
    return data;
  },

  getAnalytics: async (id: string): Promise<any> => {
    const { data } = await api.get(`/api/packages/${id}/analytics`);
    return data;
  }
}; 