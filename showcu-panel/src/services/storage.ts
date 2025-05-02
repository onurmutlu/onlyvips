import { api } from './api';

export interface StorageFile {
  id: string;
  name: string;
  url: string;
  size: number;
  type: string;
  createdAt: Date;
}

export interface UploadFileData {
  file: File;
  type: 'image' | 'video';
}

export const storageService = {
  upload: async (data: UploadFileData): Promise<StorageFile> => {
    const formData = new FormData();
    formData.append('file', data.file);
    formData.append('type', data.type);

    const { data: uploadedFile } = await api.post('/api/storage/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return uploadedFile;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/storage/${id}`);
  },

  getById: async (id: string): Promise<StorageFile> => {
    const { data } = await api.get(`/api/storage/${id}`);
    return data;
  },

  getAll: async (): Promise<StorageFile[]> => {
    const { data } = await api.get('/api/storage');
    return data;
  }
}; 