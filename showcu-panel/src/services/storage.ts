import api from './api';

interface UploadResponse {
  url: string;
  key: string;
}

export const storageService = {
  async uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post<UploadResponse>('/storage/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  async uploadImage(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('image', file);

    const response = await api.post<UploadResponse>('/storage/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  async uploadVideo(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('video', file);

    const response = await api.post<UploadResponse>('/storage/upload/video', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  async uploadAudio(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('audio', file);

    const response = await api.post<UploadResponse>('/storage/upload/audio', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  async deleteFile(key: string): Promise<void> {
    await api.delete(`/storage/${key}`);
  },

  async getFileUrl(key: string): Promise<string> {
    const response = await api.get(`/storage/${key}/url`);
    return response.data.url;
  }
}; 