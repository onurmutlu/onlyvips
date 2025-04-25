import { api } from './api';

export interface AnalyticsData {
  totalViews: number;
  totalSubscribers: number;
  totalRevenue: number;
  contentViews: {
    id: string;
    title: string;
    views: number;
    revenue: number;
  }[];
  subscriberGrowth: {
    date: string;
    count: number;
  }[];
  revenueByDate: {
    date: string;
    amount: number;
  }[];
}

export const analyticsService = {
  async getOverview(): Promise<AnalyticsData> {
    const response = await api.get('/analytics/overview');
    return response.data;
  },

  async getContentAnalytics(contentId: string): Promise<{
    views: number;
    revenue: number;
    viewsByDate: { date: string; count: number }[];
  }> {
    const response = await api.get(`/analytics/content/${contentId}`);
    return response.data;
  },

  async getSubscriberAnalytics(): Promise<{
    total: number;
    growth: { date: string; count: number }[];
  }> {
    const response = await api.get('/analytics/subscribers');
    return response.data;
  },

  async getRevenueAnalytics(): Promise<{
    total: number;
    byDate: { date: string; amount: number }[];
  }> {
    const response = await api.get('/analytics/revenue');
    return response.data;
  }
}; 