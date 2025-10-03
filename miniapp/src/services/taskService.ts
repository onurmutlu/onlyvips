import { Task, TaskStatus, TaskType, UserTask, checkReferralFromTelegramData } from '../types/task';
import api from '../api/apiClient';

// Kullanıcıya ait görevleri yükle
export const fetchUserTasks = async (userId: string): Promise<UserTask[]> => {
  try {
    // Gerçek API çağrısı
    const response = await api.user.getTaskStatus(userId, 'all');
    if (response.success && response.data) {
      return response.data;
    }
    
    // Fallback - Demo veriler
    return getDemoUserTasks(userId);
  } catch (error) {
    console.error('Görevler yüklenirken hata oluştu:', error);
    return [];
  }
};

// Tüm görevleri yükle
export const fetchAllTasks = async (): Promise<Task[]> => {
  try {
    // Gerçek API çağrısı burada yapılacak
    const response = await api.creators.getTaskById('all');
    if (response.success && response.data) {
      return response.data;
    }
    
    // Fallback - Demo veriler
    return getDemoTasks();
  } catch (error) {
    console.error('Görevler yüklenirken hata oluştu:', error);
    return [];
  }
};

// Belirli bir görevi yükle
export const fetchTaskById = async (taskId: string): Promise<Task | null> => {
  try {
    // Gerçek API çağrısı
    const response = await api.creators.getTaskById(taskId);
    if (response.success && response.data) {
      return response.data;
    }
    
    // Fallback - Demo veriler
    const demoTasks = getDemoTasks();
    return demoTasks.find(task => task.id === taskId) || null;
  } catch (error) {
    console.error(`${taskId} ID'li görev yüklenirken hata oluştu:`, error);
    return null;
  }
};

// Bir görevi tamamla
export const completeTask = async (userId: string, taskId: string): Promise<boolean> => {
  try {
    // Gerçek API çağrısı
    const response = await api.user.completeTask(userId, taskId);
    return response.success;
  } catch (error) {
    console.error(`${taskId} ID'li görev tamamlanırken hata oluştu:`, error);
    return false;
  }
};

// Referral görevini kontrol et ve tamamla
export const checkAndCompleteReferralTask = async (userId: string): Promise<boolean> => {
  try {
    // Telegram initData'dan referral bilgisini kontrol et
    const referralUserId = checkReferralFromTelegramData();
    
    if (!referralUserId) {
      return false;
    }
    
    // Referral görevi bul
    const tasks = await fetchAllTasks();
    const referralTask = tasks.find(task => task.type === TaskType.REFERRAL);
    
    if (!referralTask) {
      return false;
    }
    
    // Görevi tamamla
    return await completeTask(referralUserId, referralTask.id);
  } catch (error) {
    console.error('Referral görevi tamamlanırken hata oluştu:', error);
    return false;
  }
};

// Demo görevler
const getDemoTasks = (): Task[] => {
  return [
    {
      id: 'task1',
      title: 'Bir Arkadaşını Davet Et',
      description: 'Özel referral linkinle bir arkadaşını OnlyVips\'e davet et.',
      type: TaskType.REFERRAL,
      verificationMethod: 'automatic',
      rewards: [
        {
          type: 'token',
          amount: 15,
          description: 'Jeton ödülü'
        },
        {
          type: 'xp',
          amount: 50,
          description: 'XP ödülü'
        }
      ],
      requiredActions: {
        referralCount: 1
      },
      creatorId: 'system',
      createdAt: Date.now() - 1000 * 60 * 60 * 24 * 7 // 1 hafta önce
    },
    {
      id: 'task2',
      title: 'Premium İçerik Satın Al',
      description: 'Herhangi bir premium içeriğe erişim satın al ve özel rozet kazan.',
      type: TaskType.CONTENT_PURCHASE,
      verificationMethod: 'automatic',
      rewards: [
        {
          type: 'badge',
          amount: 1,
          description: 'Premium İçerik Rozeti',
          badgeId: 'premium_content_badge'
        },
        {
          type: 'xp',
          amount: 100,
          description: 'XP ödülü'
        }
      ],
      creatorId: 'system',
      createdAt: Date.now() - 1000 * 60 * 60 * 24 * 3 // 3 gün önce
    }
  ];
};

// Demo kullanıcı görevleri
const getDemoUserTasks = (userId: string): UserTask[] => {
  return [
    {
      userId,
      taskId: 'task1',
      status: TaskStatus.PENDING,
      rewardsIssued: false
    },
    {
      userId,
      taskId: 'task2',
      status: TaskStatus.COMPLETED,
      completedAt: Date.now() - 1000 * 60 * 60, // 1 saat önce
      verifiedAt: Date.now() - 1000 * 60 * 30, // 30 dakika önce
      rewardsIssued: true
    }
  ];
}; 