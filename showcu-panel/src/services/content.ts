import { api } from './api';

export interface Content {
  id: string;
  title: string;
  description: string;
  mediaUrl: string;
  mediaType: 'image' | 'video';
  isPremium: boolean;
  price: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface CreateContentData {
  title: string;
  description: string;
  mediaUrl: string;
  mediaType: 'image' | 'video';
  isPremium: boolean;
  price: number;
}

export const contentService = {
  getAll: async (): Promise<Content[]> => {
    const { data } = await api.get('/api/content');
    return data;
  },

  getById: async (id: string): Promise<Content> => {
    const { data } = await api.get(`/api/content/${id}`);
    return data;
  },

  create: async (data: CreateContentData): Promise<Content> => {
    const { data: response } = await api.post('/api/content', data);
    return response;
  },

  update: async (id: string, data: Partial<CreateContentData>): Promise<Content> => {
    const { data: response } = await api.put(`/api/content/${id}`, data);
    return response;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/content/${id}`);
  },

  getAnalytics: async (id: string) => {
    const { data } = await api.get(`/api/content/${id}/analytics`);
    return data;
  },
}; 