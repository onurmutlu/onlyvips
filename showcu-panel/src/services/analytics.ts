import { api } from './api';

export interface AnalyticsData {
  totalUsers: number;
  totalSubscribers: number;
  totalRevenue: number;
  activePackages: number;
  totalContent: number;
  monthlyRevenue: {
    month: string;
    revenue: number;
  }[];
  topPackages: {
    id: string;
    name: string;
    subscribers: number;
    revenue: number;
  }[];
  topContent: {
    id: string;
    title: string;
    views: number;
    revenue: number;
  }[];
}

export interface AnalyticsOverview {
  totalViews: number;
  totalSubscribers: number;
  totalRevenue: number;
  recentContent: Array<{
    id: string;
    title: string;
    views: number;
    revenue: number;
  }>;
}

export const analyticsService = {
  getDashboard: async (): Promise<AnalyticsData> => {
    const { data } = await api.get('/api/analytics/dashboard');
    return data;
  },

  getRevenue: async (startDate: string, endDate: string): Promise<any> => {
    const { data } = await api.get('/api/analytics/revenue', {
      params: { startDate, endDate }
    });
    return data;
  },

  getSubscribers: async (startDate: string, endDate: string): Promise<any> => {
    const { data } = await api.get('/api/analytics/subscribers', {
      params: { startDate, endDate }
    });
    return data;
  },

  getContent: async (startDate: string, endDate: string): Promise<any> => {
    const { data } = await api.get('/api/analytics/content', {
      params: { startDate, endDate }
    });
    return data;
  },

  getOverview: async (): Promise<AnalyticsOverview> => {
    const response = await api.get('/api/analytics/overview');
    return response.data;
  },

  getContentAnalytics: async (contentId: string) => {
    const response = await api.get(`/api/analytics/content/${contentId}`);
    return response.data;
  },

  getRevenueAnalytics: async (period: 'day' | 'week' | 'month' | 'year') => {
    const response = await api.get(`/api/analytics/revenue?period=${period}`);
    return response.data;
  }
}; 