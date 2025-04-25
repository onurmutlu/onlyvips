import api from './api';

interface Content {
  id: string;
  title: string;
  description: string;
  mediaUrl: string;
  mediaType: 'image' | 'video' | 'audio';
  isPremium: boolean;
  price: number;
  createdAt: string;
  updatedAt: string;
}

interface CreateContentData {
  title: string;
  description: string;
  mediaUrl: string;
  mediaType: 'image' | 'video' | 'audio';
  isPremium: boolean;
  price: number;
}

export const contentService = {
  async getAll() {
    const response = await api.get<Content[]>('/content');
    return response.data;
  },

  async getById(id: string) {
    const response = await api.get<Content>(`/content/${id}`);
    return response.data;
  },

  async create(data: CreateContentData) {
    const response = await api.post<Content>('/content', data);
    return response.data;
  },

  async update(id: string, data: Partial<CreateContentData>) {
    const response = await api.put<Content>(`/content/${id}`, data);
    return response.data;
  },

  async delete(id: string) {
    await api.delete(`/content/${id}`);
  },

  async getAnalytics(id: string) {
    const response = await api.get(`/content/${id}/analytics`);
    return response.data;
  }
}; 