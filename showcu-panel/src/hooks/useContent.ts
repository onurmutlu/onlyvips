import { create } from 'zustand';
import { contentService } from '../services';

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

interface ContentState {
  contents: Content[];
  loading: boolean;
  error: string | null;
  fetchContents: () => Promise<void>;
  createContent: (data: {
    title: string;
    description: string;
    mediaUrl: string;
    mediaType: 'image' | 'video' | 'audio';
    isPremium: boolean;
    price: number;
  }) => Promise<void>;
  updateContent: (id: string, data: Partial<Content>) => Promise<void>;
  deleteContent: (id: string) => Promise<void>;
}

export const useContent = create<ContentState>((set) => ({
  contents: [],
  loading: false,
  error: null,
  fetchContents: async () => {
    try {
      set({ loading: true, error: null });
      const contents = await contentService.getAll();
      set({ contents, loading: false });
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
    }
  },
  createContent: async (data) => {
    try {
      set({ loading: true, error: null });
      const newContent = await contentService.create(data);
      set((state) => ({
        contents: [...state.contents, newContent],
        loading: false
      }));
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
    }
  },
  updateContent: async (id, data) => {
    try {
      set({ loading: true, error: null });
      const updatedContent = await contentService.update(id, data);
      set((state) => ({
        contents: state.contents.map((content) =>
          content.id === id ? updatedContent : content
        ),
        loading: false
      }));
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
    }
  },
  deleteContent: async (id) => {
    try {
      set({ loading: true, error: null });
      await contentService.delete(id);
      set((state) => ({
        contents: state.contents.filter((content) => content.id !== id),
        loading: false
      }));
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
    }
  }
})); 