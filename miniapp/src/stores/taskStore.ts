import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import api from '../api/apiClient';

// Görev Tip Tanımları
export interface Task {
  id: string;
  title: string;
  description?: string;
  taskType: 'follow' | 'message' | 'watch' | 'other';
  reward: number; // Token ödülü
  xpReward: number; // XP ödülü
  creatorId: string;
  isActive: boolean;
  completionCount?: number;
  createdAt: string;
  requiredFor?: string[]; // Bu görevin gerekli olduğu içerik ID'leri
}

// Store State Tipi
interface TaskState {
  tasks: Task[];
  activeTaskId: string | null;
  loading: boolean;
  error: string | null;
}

// Store Aksiyonları
interface TaskActions {
  // Görevleri backend'den yükle
  fetchTasks: () => Promise<void>;
  
  // Kullanıcı için önerilen görevleri al
  fetchRecommendedTasks: (userId: string) => Promise<void>;
  
  // Belirli bir içerik üreticisinin görevlerini al
  fetchCreatorTasks: (creatorId: string) => Promise<void>;
  
  // Görev tamamlama durumu
  startTask: (taskId: string) => void;
  
  // Görev detaylarını getir
  getTaskById: (taskId: string) => Task | undefined;
  
  // Belirli bir içerik için gerekli görevleri filtrele
  getTasksForContent: (contentId: string) => Task[];
  
  // Hata durumunu temizle
  clearError: () => void;
  
  // Görevleri sıfırla
  resetTasks: () => void;
}

// Tam Store Tipi
type TaskStore = TaskState & TaskActions;

// Store Oluşturma
export const useTaskStore = create<TaskStore>()(
  persist(
    (set, get) => ({
      // Başlangıç State
      tasks: [],
      activeTaskId: null,
      loading: false,
      error: null,
      
      // Tüm görevleri getir
      fetchTasks: async () => {
        set({ loading: true, error: null });
        
        try {
          const response = await api.content.getCategories();
          
          if (response.success && response.data) {
            set({ tasks: response.data, loading: false });
          } else {
            set({ error: 'Görevler yüklenirken bir hata oluştu', loading: false });
          }
        } catch (error) {
          console.error('Görev yükleme hatası:', error);
          set({ 
            error: 'Görevler yüklenirken teknik bir hata oluştu', 
            loading: false 
          });
        }
      },
      
      // Kullanıcıya özel görevleri getir
      fetchRecommendedTasks: async (userId) => {
        set({ loading: true, error: null });
        
        try {
          // Burada uygun API çağrısı yapılmalı
          // Şu anda demo veriler ekliyoruz
          const demoTasks: Task[] = [
            {
              id: 'task1',
              title: 'İçerik Üreticisini takip et',
              description: 'Sevdiğin içerik üreticilerini takip ederek destek ol',
              taskType: 'follow',
              reward: 5,
              xpReward: 10,
              creatorId: 'creator1',
              isActive: true,
              createdAt: new Date().toISOString()
            },
            {
              id: 'task2',
              title: 'İçerik Üreticisine mesaj gönder',
              description: 'Destek olmak için içerik üreticisine mesaj gönder',
              taskType: 'message',
              reward: 10,
              xpReward: 15,
              creatorId: 'creator1',
              isActive: true,
              createdAt: new Date().toISOString()
            }
          ];
          
          set({ 
            tasks: demoTasks, 
            loading: false 
          });
        } catch (error) {
          console.error('Görev yükleme hatası:', error);
          set({ 
            error: 'Görevler yüklenirken teknik bir hata oluştu', 
            loading: false 
          });
        }
      },
      
      // Belirli bir içerik üreticisinin görevlerini getir
      fetchCreatorTasks: async (creatorId) => {
        set({ loading: true, error: null });
        
        try {
          // API'den gerçek veri çekmek yerine şu anda demo veriler kullanıyoruz
          // Gerçek uygulamada bu API çağrısı yapılmalı
          // const response = await api.creators.getCreatorTasks(creatorId);
          
          const demoTasks: Task[] = [
            {
              id: 'task1',
              title: 'Demo Görev 1',
              taskType: 'follow',
              reward: 5,
              xpReward: 10,
              creatorId,
              isActive: true,
              createdAt: new Date().toISOString()
            }
          ];
          
          set({ 
            tasks: demoTasks, 
            loading: false 
          });
        } catch (error) {
          console.error('Görev yükleme hatası:', error);
          set({ 
            error: 'Görevler yüklenirken teknik bir hata oluştu', 
            loading: false 
          });
        }
      },
      
      // Kullanıcı bir göreve başladı
      startTask: (taskId) => {
        set({ activeTaskId: taskId });
      },
      
      // ID'ye göre görev getir
      getTaskById: (taskId) => {
        return get().tasks.find(task => task.id === taskId);
      },
      
      // İçerik için gerekli görevleri getir
      getTasksForContent: (contentId) => {
        return get().tasks.filter(
          task => task.requiredFor?.includes(contentId)
        );
      },
      
      // Hata durumunu temizle
      clearError: () => {
        set({ error: null });
      },
      
      // Görevleri sıfırla
      resetTasks: () => {
        set({ 
          tasks: [],
          activeTaskId: null,
          loading: false,
          error: null
        });
      }
    }),
    {
      name: 'onlyvips-tasks-storage'
    }
  )
); 