import api from './index';
import { Content } from '../types';

export interface ContentListParams {
  page?: number;
  limit?: number;
  category?: string;
  showcuId?: string;
  isPremium?: boolean;
  search?: string;
}

export interface ContentListResponse {
  contents: Content[];
  pagination: {
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  };
}

export interface ContentDetailResponse {
  content: Content;
  owner: {
    telegramId: string;
    username?: string;
    firstName?: string;
    lastName?: string;
    profilePhoto?: string;
  } | null;
}

// İçerik listesi al
export const getContentList = async (params: ContentListParams = {}): Promise<ContentListResponse> => {
  const response = await api.get<ContentListResponse>('/api/content', { params });
  return response.data;
};

// İçerik detayı al
export const getContentDetail = async (id: string): Promise<ContentDetailResponse> => {
  const response = await api.get<ContentDetailResponse>(`/api/content/${id}`);
  return response.data;
};

// İçerik oluştur
export const createContent = async (contentData: Partial<Content>): Promise<{ content: Content }> => {
  const response = await api.post<{ content: Content }>('/api/content', contentData);
  return response.data;
};

// İçeriği güncelle
export const updateContent = async (id: string, contentData: Partial<Content>): Promise<{ content: Content }> => {
  const response = await api.put<{ content: Content }>(`/api/content/${id}`, contentData);
  return response.data;
};

// İçeriği sil
export const deleteContent = async (id: string): Promise<{ message: string }> => {
  const response = await api.delete<{ message: string }>(`/api/content/${id}`);
  return response.data;
}; 