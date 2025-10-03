import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from 'react-router-dom';
import { useUserStore } from '../stores/userStore';
import { fetchTaskById } from '../services/taskService';
import { completeTask } from '../services/taskService';
import { Task, TaskStatus, TaskType, UserTask } from '../types/task';
import { Badge } from '../types/badge';
import { fetchUserBadges } from '../services/badgeService';

// Doğrulama tipi açıklamaları
const verificationDescriptions: Record<string, string> = {
  "invite_tracker": "Davet bağlantısı ile yeni kullanıcı davet etmelisiniz.",
  "message_forward": "Mesajı belirtilen kanala iletmelisiniz.",
  "bot_mention": "Botu belirtilen grupta etiketlemelisiniz.",
  "deeplink_track": "Özel bağlantıyı paylaşmalısınız.",
  "pin_check": "Mesajı grubunuzda sabitlemelisiniz.",
  "post_share": "Gönderiyi kendi profilinizde paylaşmalısınız.",
  "share_count": "İçeriği en az belirtilen sayıda kişiye iletmelisiniz.",
  "referral": "Referans kodunuzu kullanarak yeni üye kazandırmalısınız."
};

const TaskDetail: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();
  const { telegramId, userTasks, updateUserTask } = useUserStore();
  
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [userTask, setUserTask] = useState<UserTask | null>(null);
  const [completingTask, setCompletingTask] = useState(false);
  const [badges, setBadges] = useState<Badge[]>([]);
  
  useEffect(() => {
    const loadTaskDetails = async () => {
      if (!taskId) return;
      
      setLoading(true);
      try {
        // Görevi yükle
        const taskData = await fetchTaskById(taskId);
        if (taskData) {
          setTask(taskData);
          
          // Kullanıcının görev durumunu bul
          const userTaskData = userTasks.find(task => task.taskId === taskId);
          if (userTaskData) {
            setUserTask(userTaskData);
          }
          
          // Rozetleri yükle
          const badgesData = await fetchUserBadges(telegramId);
          setBadges(badgesData);
        }
      } catch (error) {
        console.error("Görev detayları yüklenirken hata oluştu:", error);
      } finally {
        setLoading(false);
      }
    };
    
    loadTaskDetails();
  }, [taskId, telegramId, userTasks]);
  
  // Görevi tamamla
  const handleCompleteTask = async () => {
    if (!task || !telegramId) return;
    
    setCompletingTask(true);
    try {
      const success = await completeTask(telegramId, task.id);
      
      if (success) {
        // Görev durumunu güncelle
        const updatedUserTask: UserTask = {
          userId: telegramId,
          taskId: task.id,
          status: TaskStatus.COMPLETED,
          completedAt: Date.now(),
          rewardsIssued: true
        };
        
        setUserTask(updatedUserTask);
        updateUserTask(updatedUserTask);
        
        // Rozetleri yeniden yükle (Rozet ödülü varsa görmek için)
        const badgesData = await fetchUserBadges(telegramId);
        setBadges(badgesData);
      }
    } catch (error) {
      console.error("Görev tamamlanırken hata oluştu:", error);
    } finally {
      setCompletingTask(false);
    }
  };
  
  // Görev tipine göre ikon seç
  const getTaskIcon = (type: TaskType) => {
    switch (type) {
      case TaskType.CONTENT_VIEW: return '👁️';
      case TaskType.CONTENT_PURCHASE: return '🛒';
      case TaskType.REFERRAL: return '👥';
      case TaskType.SOCIAL_SHARE: return '🔄';
      case TaskType.COMMENT: return '💬';
      case TaskType.APP_USAGE: return '📱';
      case TaskType.SUBSCRIPTION: return '⭐';
      default: return '🎯';
    }
  };
  
  // Referral linki oluştur
  const generateReferralLink = () => {
    if (!telegramId) return '';
    
    const baseUrl = 'https://t.me/OnlyVipsBot';
    return `${baseUrl}?start=referral_${telegramId}`;
  };
  
  // Telegram ile paylaş
  const shareWithTelegram = () => {
    const tg = window.Telegram?.WebApp;
    if (!tg) return;
    
    const referralLink = generateReferralLink();
    tg.sendData(JSON.stringify({
      type: 'share_referral',
      data: {
        text: `OnlyVips'e katıl ve özel içeriklere eriş! ${referralLink}`,
        url: referralLink
      }
    }));
  };
  
  // Buton metni belirle
  const getButtonText = () => {
    if (!task) return 'Yükleniyor...';
    
    if (userTask?.status === TaskStatus.COMPLETED || userTask?.status === TaskStatus.VERIFIED) {
      return 'Tamamlandı ✓';
    }
    
    switch (task.type) {
      case TaskType.REFERRAL:
        return 'Davet Linki Paylaş';
      case TaskType.CONTENT_PURCHASE:
        return 'İçeriğe Git';
      case TaskType.SOCIAL_SHARE:
        return 'Paylaş';
      default:
        return 'Görevi Tamamla';
    }
  };
  
  // Buton tıklama işlevi
  const handleButtonClick = () => {
    if (!task) return;
    
    if (userTask?.status === TaskStatus.COMPLETED || userTask?.status === TaskStatus.VERIFIED) {
      return; // Görev zaten tamamlanmış
    }
    
    switch (task.type) {
      case TaskType.REFERRAL:
        shareWithTelegram();
        break;
      case TaskType.CONTENT_PURCHASE:
        // İçerik sayfasına yönlendir
        if (task.requiredActions?.contentId) {
          navigate(`/content/${task.requiredActions.contentId}`);
        }
        break;
      default:
        handleCompleteTask();
        break;
    }
  };
  
  // Yükleme durumu
  if (loading) {
    return (
      <div className="min-h-screen pt-24 p-4 bg-gradient-to-br from-black via-gray-900 to-gray-800 text-white">
        <div className="container mx-auto max-w-md">
          <div className="flex items-center mb-6">
            <button 
              onClick={() => navigate('/')}
              className="mr-4 text-gray-400 hover:text-white transition-colors"
            >
              ← Geri
            </button>
            <div className="h-7 bg-gray-700/50 rounded w-1/3 animate-pulse"></div>
          </div>
          
          <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-6 animate-pulse">
            <div className="h-10 bg-gray-700/50 rounded w-3/4 mb-4"></div>
            <div className="h-4 bg-gray-700/50 rounded w-full mb-2"></div>
            <div className="h-4 bg-gray-700/50 rounded w-5/6 mb-6"></div>
            
            <div className="h-16 bg-gray-700/30 rounded-lg mb-6"></div>
            
            <div className="h-12 bg-gray-700/50 rounded-lg"></div>
          </div>
        </div>
      </div>
    );
  }
  
  // Görev yoksa
  if (!task) {
    return (
      <div className="min-h-screen pt-24 p-4 bg-gradient-to-br from-black via-gray-900 to-gray-800 text-white">
        <div className="container mx-auto max-w-md text-center">
          <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-6">
            <div className="text-4xl mb-2">🔍</div>
            <h3 className="text-xl font-medium text-white mb-2">Görev Bulunamadı</h3>
            <p className="text-gray-400 mb-4">
              İstediğiniz görev bulunamadı veya artık mevcut değil.
            </p>
            <button 
              onClick={() => navigate('/')}
              className="bg-white/10 hover:bg-white/20 text-white px-4 py-2 rounded-lg transition-colors"
            >
              Ana Sayfaya Dön
            </button>
          </div>
        </div>
      </div>
    );
  }
  
  // Görev detayı
  return (
    <div className="min-h-screen pt-24 p-4 bg-gradient-to-br from-black via-gray-900 to-gray-800 text-white">
      <div className="container mx-auto max-w-md">
        <div className="flex items-center mb-6">
          <button 
            onClick={() => navigate('/')}
            className="mr-4 text-gray-400 hover:text-white transition-colors"
          >
            ← Geri
          </button>
          <h1 className="text-2xl font-bold text-white">Görev Detayı</h1>
        </div>
        
        <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-6 mb-6">
          <div className="flex items-center mb-4">
            <div className="w-12 h-12 rounded-full flex items-center justify-center text-xl bg-gray-800/50 border border-white/10 mr-3">
              {getTaskIcon(task.type)}
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">{task.title}</h2>
              <div className="text-sm text-gray-400">
                {task.type === TaskType.REFERRAL ? 'Arkadaş Daveti' : 
                 task.type === TaskType.CONTENT_PURCHASE ? 'İçerik Satın Alma' : 
                 task.type === TaskType.SOCIAL_SHARE ? 'Sosyal Paylaşım' : 
                 'Platform Görevi'}
              </div>
            </div>
          </div>
          
          <p className="text-gray-300 mb-6">{task.description}</p>
          
          {/* Görev durumu */}
          {userTask?.status && (
            <div className="mb-5 px-4 py-3 rounded-lg bg-gray-800/30 border border-white/5">
              <div className="text-sm text-gray-400 mb-1">Görev Durumu</div>
              <div className="flex items-center">
                <div 
                  className={`w-2 h-2 rounded-full mr-2 ${
                    userTask.status === TaskStatus.COMPLETED || userTask.status === TaskStatus.VERIFIED 
                      ? 'bg-green-400' 
                      : userTask.status === TaskStatus.PENDING 
                      ? 'bg-yellow-400'
                      : 'bg-red-400'
                  }`}
                ></div>
                <div className="text-white">
                  {userTask.status === TaskStatus.COMPLETED ? 'Tamamlandı' :
                   userTask.status === TaskStatus.VERIFIED ? 'Doğrulandı' :
                   userTask.status === TaskStatus.PENDING ? 'Beklemede' :
                   userTask.status === TaskStatus.EXPIRED ? 'Süresi Doldu' : 'Başarısız'}
                </div>
              </div>
            </div>
          )}
          
          {/* Ödüller */}
          <div className="mb-6">
            <h3 className="text-white font-medium mb-2">Ödüller</h3>
            <div className="grid grid-cols-2 gap-3">
              {task.rewards.map((reward, index) => (
                <div 
                  key={index}
                  className="bg-gray-800/30 border border-white/5 rounded-lg p-3 flex items-center"
                >
                  <div className="w-8 h-8 rounded-full flex items-center justify-center mr-2 text-lg bg-gray-700/30">
                    {reward.type === 'token' ? '💎' : 
                     reward.type === 'xp' ? '⚡' : 
                     reward.type === 'badge' ? '🏆' :
                     reward.type === 'content_access' ? '🔓' : '🎁'}
                  </div>
                  <div>
                    <div className="text-sm text-gray-300">
                      {reward.type === 'token' ? `${reward.amount} Token` : 
                       reward.type === 'xp' ? `${reward.amount} XP` : 
                       reward.type === 'badge' ? 'Özel Rozet' :
                       reward.type === 'content_access' ? 'İçerik Erişimi' : 
                       reward.description || 'Ödül'}
                    </div>
                    {reward.description && reward.type !== 'token' && reward.type !== 'xp' && (
                      <div className="text-xs text-gray-400">{reward.description}</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* Doğrulama gereksinimleri */}
          {task.type === TaskType.REFERRAL && (
            <div className="mb-6">
              <h3 className="text-white font-medium mb-2">Doğrulama</h3>
              <div className="bg-gray-800/30 border border-white/5 rounded-lg p-4">
                <p className="text-gray-300 text-sm">
                  Bu görevi tamamlamak için, referral linkinizi kullanarak en az 
                  {task.requiredActions?.referralCount || 1} kişinin uygulamaya katılması gerekmektedir.
                </p>
              </div>
            </div>
          )}
          
          {/* Görev tamamlama butonu */}
          <button
            onClick={handleButtonClick}
            disabled={userTask?.status === TaskStatus.COMPLETED || userTask?.status === TaskStatus.VERIFIED || completingTask}
            className={`w-full py-3 px-4 rounded-lg font-medium transition-all 
              ${userTask?.status === TaskStatus.COMPLETED || userTask?.status === TaskStatus.VERIFIED
                ? 'bg-green-500/20 text-green-400 cursor-default'
                : 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-700 hover:to-indigo-700 active:scale-[0.98]'
              } ${completingTask ? 'opacity-70' : 'opacity-100'}`}
          >
            {completingTask ? 'İşleniyor...' : getButtonText()}
          </button>
        </div>
        
        {/* Referral link paylaşımı */}
        {task.type === TaskType.REFERRAL && (
          <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-5">
            <h3 className="text-white font-medium mb-2">Referral Linkiniz</h3>
            <div className="relative mb-4">
              <input 
                type="text"
                readOnly
                value={generateReferralLink()}
                className="w-full bg-gray-800/50 border border-white/10 rounded-lg px-3 py-2 text-gray-300 text-sm focus:outline-none focus:border-blue-500/50"
              />
              <button 
                onClick={() => {
                  navigator.clipboard.writeText(generateReferralLink());
                  // Kopyalama bildirimi gösterilebilir
                }}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 text-xs bg-white/10 hover:bg-white/20 text-white px-2 py-1 rounded"
              >
                Kopyala
              </button>
            </div>
            <p className="text-gray-400 text-sm">
              Arkadaşlarınızı davet etmek için bu linki paylaşın. Her başarılı davet için ödül kazanacaksınız.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default TaskDetail;
