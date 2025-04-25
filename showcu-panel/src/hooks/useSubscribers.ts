import { create } from 'zustand';
import { subscriberService } from '../services';

interface Subscriber {
  id: string;
  userId: string;
  username: string;
  packageId: string;
  packageName: string;
  startDate: string;
  endDate: string;
  status: 'active' | 'expired' | 'cancelled';
  createdAt: string;
  updatedAt: string;
}

interface SubscribersState {
  subscribers: Subscriber[];
  loading: boolean;
  error: string | null;
  fetchSubscribers: () => Promise<void>;
  fetchSubscribersByPackage: (packageId: string) => Promise<void>;
  createSubscriber: (data: {
    userId: string;
    packageId: string;
  }) => Promise<void>;
  updateSubscriber: (id: string, data: Partial<Subscriber>) => Promise<void>;
  deleteSubscriber: (id: string) => Promise<void>;
}

export const useSubscribers = create<SubscribersState>((set) => ({
  subscribers: [],
  loading: false,
  error: null,
  fetchSubscribers: async () => {
    try {
      set({ loading: true, error: null });
      const subscribers = await subscriberService.getAll();
      set({ subscribers, loading: false });
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
    }
  },
  fetchSubscribersByPackage: async (packageId: string) => {
    try {
      set({ loading: true, error: null });
      const subscribers = await subscriberService.getByPackageId(packageId);
      set({ subscribers, loading: false });
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
    }
  },
  createSubscriber: async (data) => {
    try {
      set({ loading: true, error: null });
      const newSubscriber = await subscriberService.create(data);
      set((state) => ({
        subscribers: [...state.subscribers, newSubscriber],
        loading: false
      }));
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
    }
  },
  updateSubscriber: async (id, data) => {
    try {
      set({ loading: true, error: null });
      const updatedSubscriber = await subscriberService.update(id, data);
      set((state) => ({
        subscribers: state.subscribers.map((subscriber) =>
          subscriber.id === id ? updatedSubscriber : subscriber
        ),
        loading: false
      }));
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
    }
  },
  deleteSubscriber: async (id) => {
    try {
      set({ loading: true, error: null });
      await subscriberService.delete(id);
      set((state) => ({
        subscribers: state.subscribers.filter((subscriber) => subscriber.id !== id),
        loading: false
      }));
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
    }
  }
})); 