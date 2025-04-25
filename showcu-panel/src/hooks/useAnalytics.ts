import { create } from 'zustand';
import { analyticsService } from '../services';

interface Analytics {
  totalSubscribers: number;
  activeSubscribers: number;
  totalRevenue: number;
  monthlyRevenue: number;
  contentViews: number;
  premiumContentViews: number;
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

interface AnalyticsState {
  analytics: Analytics | null;
  loading: boolean;
  error: string | null;
  fetchOverview: () => Promise<void>;
  fetchRevenue: (startDate: string, endDate: string) => Promise<void>;
  fetchSubscriberGrowth: (startDate: string, endDate: string) => Promise<void>;
  fetchContentPerformance: (startDate: string, endDate: string) => Promise<void>;
  fetchPackagePerformance: (startDate: string, endDate: string) => Promise<void>;
}

export const useAnalytics = create<AnalyticsState>((set) => ({
  analytics: null,
  loading: false,
  error: null,
  fetchOverview: async () => {
    try {
      set({ loading: true, error: null });
      const analytics = await analyticsService.getOverview();
      set({ analytics, loading: false });
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
    }
  },
  fetchRevenue: async (startDate: string, endDate: string) => {
    try {
      set({ loading: true, error: null });
      const analytics = await analyticsService.getRevenue(startDate, endDate);
      set({ analytics, loading: false });
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
    }
  },
  fetchSubscriberGrowth: async (startDate: string, endDate: string) => {
    try {
      set({ loading: true, error: null });
      const analytics = await analyticsService.getSubscriberGrowth(startDate, endDate);
      set({ analytics, loading: false });
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
    }
  },
  fetchContentPerformance: async (startDate: string, endDate: string) => {
    try {
      set({ loading: true, error: null });
      const analytics = await analyticsService.getContentPerformance(startDate, endDate);
      set({ analytics, loading: false });
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
    }
  },
  fetchPackagePerformance: async (startDate: string, endDate: string) => {
    try {
      set({ loading: true, error: null });
      const analytics = await analyticsService.getPackagePerformance(startDate, endDate);
      set({ analytics, loading: false });
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
    }
  }
})); 