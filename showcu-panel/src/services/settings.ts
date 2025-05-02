import { api } from './api';

export interface Settings {
  id: string;
  key: string;
  value: any;
  description: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface UpdateSettingsData {
  value: any;
}

export const settingsService = {
  getAll: async (): Promise<Settings[]> => {
    const { data } = await api.get('/api/settings');
    return data;
  },

  getByKey: async (key: string): Promise<Settings> => {
    const { data } = await api.get(`/api/settings/${key}`);
    return data;
  },

  update: async (key: string, data: UpdateSettingsData): Promise<Settings> => {
    const { data: updatedSettings } = await api.put(`/api/settings/${key}`, data);
    return updatedSettings;
  },

  getAnalytics: async (): Promise<any> => {
    const { data } = await api.get('/api/settings/analytics');
    return data;
  }
}; 