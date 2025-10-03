import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import api from '../api/apiClient';

// Store için tip tanımları
export interface User {
  telegramId: string | null;
  username: string | null;
  fullName: string | null;
  photoUrl: string | null;
  xp: number;
  tokens: number;
  completedTasks: string[];
  level: number;
  showXpAnimation: boolean;
  lastXpGain: number;
  leveledUp: boolean;
}

// Store aksiyonları için tip tanımları
interface UserActions {
  setUserInfo: (userData: { 
    telegramId?: string; 
    username?: string; 
    fullName?: string;
    photoUrl?: string;
  }) => void;
  gainXP: (amount: number) => boolean;
  earnTokens: (amount: number) => void;
  spendTokens: (amount: number) => boolean;
  completeTask: (taskId: string, xpReward?: number, tokenReward?: number) => boolean;
  completeTaskWithBackend: (taskId: string) => Promise<boolean>;
  isTaskCompleted: (taskId: string) => boolean;
  nextLevelProgress: () => { current: number; required: number; percentage: number };
  canSpendTokens: (amount: number) => boolean;
  resetUser: () => void;
  clearXpAnimation: () => void;
}

// UserStore tüm state ve aksiyonları bir araya getirir
export type UserStore = User & UserActions;

// Store oluşturma
export const useUserStore = create<UserStore>()(
  persist(
    (set, get) => ({
      // Başlangıç state değerleri
      telegramId: null,
      username: null,
      fullName: null,
      photoUrl: null,
      xp: 0,
      tokens: 0,
      completedTasks: [],
      level: 1,
      showXpAnimation: false,
      lastXpGain: 0,
      leveledUp: false,
      
      // Kullanıcı bilgilerini güncelle
      setUserInfo: (userData) => set((state) => ({
        telegramId: userData.telegramId || state.telegramId,
        username: userData.username || state.username,
        fullName: userData.fullName || state.fullName,
        photoUrl: userData.photoUrl || state.photoUrl
      })),
      
      // XP kazanma ve seviye atlama
      gainXP: (amount) => {
        let levelUp = false;
        
        set((state) => {
          const newXp = state.xp + amount;
          const newLevel = Math.floor(newXp / 100) + 1;
          
          if (newLevel > state.level) {
            levelUp = true;
          }
          
          return {
            xp: newXp,
            level: newLevel,
            showXpAnimation: true,
            lastXpGain: amount,
            leveledUp: levelUp
          };
        });
        
        // Animasyon bayrağını 6 saniye sonra kapat
        setTimeout(() => {
          get().clearXpAnimation();
        }, 6000);
        
        return levelUp;
      },
      
      // Token kazanma
      earnTokens: (amount) => set((state) => ({
        tokens: state.tokens + amount
      })),
      
      // XP animasyonu temizle
      clearXpAnimation: () => set({
        showXpAnimation: false,
        lastXpGain: 0,
        leveledUp: false
      }),
      
      // Token harcama
      spendTokens: (amount) => {
        const currentTokens = get().tokens;
        
        if (currentTokens >= amount) {
          set({ tokens: currentTokens - amount });
          return true;
        }
        
        return false;
      },
      
      // Görev tamamlama (lokal)
      completeTask: (taskId, xpReward = 0, tokenReward = 0) => {
        const isCompleted = get().completedTasks.includes(taskId);
        
        if (!isCompleted) {
          set((state) => ({
            completedTasks: [...state.completedTasks, taskId]
          }));
          
          // Ödülleri ver
          if (xpReward > 0) get().gainXP(xpReward);
          if (tokenReward > 0) get().earnTokens(tokenReward);
          
          return true;
        }
        
        return false;
      },
      
      // Görev tamamlama (Backend API ile)
      completeTaskWithBackend: async (taskId) => {
        const isCompleted = get().completedTasks.includes(taskId);
        
        // Görev zaten tamamlanmışsa tekrar tamamlanmasına gerek yok
        if (isCompleted) {
          return false;
        }
        
        try {
          // Kullanıcı ID bilgisini al
          const telegramId = get().telegramId;
          if (!telegramId) {
            console.error('Görev tamamlanamadı: Kullanıcı kimliği bulunamadı');
            return false;
          }
          
          // Backend API'ye görev tamamlama bildirimini gönder
          const response = await api.user.completeTask(telegramId, taskId);
          
          if (response.success && response.data) {
            // Backend'den gelen XP ve token ödüllerini kullan veya varsayılan değerleri kullan
            const xpReward = response.data.xpReward || 10; // Varsayılan 10 XP
            const tokenReward = response.data.tokenReward || 1; // Varsayılan 1 token
            
            // Local state'i güncelle
            set((state) => ({
              completedTasks: [...state.completedTasks, taskId]
            }));
            
            // XP ve token ödüllerini ver
            get().gainXP(xpReward);
            get().earnTokens(tokenReward);
            
            console.log(`✅ Görev tamamlandı: ${tokenReward} Token ve ${xpReward} XP kazanıldı!`);
            return true;
          } else {
            console.error('Görev tamamlanırken hata oluştu:', response.error);
            return false;
          }
        } catch (error) {
          console.error('Görev tamamlama hatası:', error);
          return false;
        }
      },
      
      // Görev tamamlama kontrolü
      isTaskCompleted: (taskId) => {
        return get().completedTasks.includes(taskId);
      },
      
      // Seviye ilerleme hesaplaması
      nextLevelProgress: () => {
        const state = get();
        const xpForNextLevel = 100; // Her seviye için sabit 100 XP
        const currentLevelXp = state.xp % 100;
        
        return {
          current: currentLevelXp,
          required: xpForNextLevel,
          percentage: Math.floor((currentLevelXp / xpForNextLevel) * 100)
        };
      },
      
      // Token harcayabilme kontrolü
      canSpendTokens: (amount) => {
        return get().tokens >= amount;
      },
      
      // Kullanıcı verilerini sıfırlama
      resetUser: () => set({
        telegramId: null,
        username: null,
        fullName: null,
        photoUrl: null,
        xp: 0,
        tokens: 0,
        completedTasks: [],
        level: 1,
        showXpAnimation: false,
        lastXpGain: 0,
        leveledUp: false
      })
    }),
    {
      name: 'onlyvips-user-storage' // localStorage'daki anahtar
    }
  )
); 