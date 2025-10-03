import React, { useEffect, useState } from 'react';
import { useUserStore } from '../stores/userStore';
import { useTaskStore, Task } from '../stores/taskStore';
import api from '../api/apiClient';
import '../styles/TaskCompletions.css';

interface TaskCompletionUser {
  id: string;
  username: string;
  avatar: string;
  completedAt: string;
}

interface TaskCompletionProps {
  taskId: string;
}

const TaskCompletions: React.FC<TaskCompletionProps> = ({ taskId }) => {
  const [completions, setCompletions] = useState<TaskCompletionUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [completing, setCompleting] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  
  const { getTaskById } = useTaskStore();
  const task = getTaskById(taskId);
  
  const { 
    xp, 
    tokens, 
    completeTaskWithBackend, 
    isTaskCompleted 
  } = useUserStore();
  
  const taskCompleted = isTaskCompleted(taskId);
  
  useEffect(() => {
    const fetchTaskCompletions = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await api.creators.getTaskCompletions('creator1', taskId);
        
        if (response.success && response.data) {
          setCompletions(response.data);
        } else {
          setError('Görev tamamlama verileri alınamadı');
        }
      } catch (error) {
        console.error('Görev tamamlama verileri alınırken hata:', error);
        setError('Bir hata oluştu');
      } finally {
        setLoading(false);
      }
    };
    
    if (taskId) {
      fetchTaskCompletions();
    }
  }, [taskId]);
  
  const handleCompleteTask = async () => {
    if (!task || taskCompleted || completing) return;
    
    setCompleting(true);
    setSuccessMessage(null);
    
    try {
      const success = await completeTaskWithBackend(taskId);
      
      if (success) {
        setSuccessMessage(`Görev başarıyla tamamlandı! ${task.reward} token ve ${task.xpReward} XP kazandınız.`);
        
        const currentUser = {
          id: Math.random().toString(36).substr(2, 9),
          username: 'Siz',
          avatar: 'https://i.pravatar.cc/150?img=22',
          completedAt: new Date().toISOString()
        };
        
        setCompletions(prev => [currentUser, ...prev]);
      } else {
        setError('Görev tamamlanamadı. Lütfen daha sonra tekrar deneyin.');
      }
    } catch (error) {
      console.error('Görev tamamlama hatası:', error);
      setError('Görev tamamlanırken bir hata oluştu.');
    } finally {
      setCompleting(false);
      
      if (successMessage) {
        setTimeout(() => {
          setSuccessMessage(null);
        }, 5000);
      }
    }
  };
  
  const getDemoCompletions = (): TaskCompletionUser[] => {
    return [
      {
        id: 'user1',
        username: 'aylin_84',
        avatar: 'https://i.pravatar.cc/150?img=1',
        completedAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
      },
      {
        id: 'user2',
        username: 'mehmet_kaya',
        avatar: 'https://i.pravatar.cc/150?img=2',
        completedAt: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString()
      },
      {
        id: 'user3',
        username: 'zeynep_demir',
        avatar: 'https://i.pravatar.cc/150?img=3',
        completedAt: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString()
      }
    ];
  };
  
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('tr-TR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };
  
  const getTimeAgo = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    
    const diffMins = Math.floor(diffMs / (1000 * 60));
    
    if (diffMins < 1) return 'Az önce';
    if (diffMins < 60) return `${diffMins} dakika önce`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours} saat önce`;
    
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays < 30) return `${diffDays} gün önce`;
    
    const diffMonths = Math.floor(diffDays / 30);
    return `${diffMonths} ay önce`;
  };
  
  const showCompletions = completions.length > 0 ? 
    completions : 
    (error ? getDemoCompletions() : []);
  
  return (
    <div className="bg-black/30 rounded-xl p-4 shadow-lg">
      <h2 className="text-lg font-semibold mb-2">
        Görevi Tamamlayanlar
        {task && (
          <span className="text-sm font-normal ml-2 text-gray-400">
            ({task.title})
          </span>
        )}
      </h2>
      
      {task && (
        <div className="mb-4 p-3 bg-black/20 rounded-lg border border-gray-800">
          <div className="text-sm text-gray-300 mb-2">
            {task.description || 'Bu görevi tamamlayarak token ve XP kazanabilirsiniz.'}
          </div>
          
          <div className="flex flex-wrap gap-2 mb-3">
            <div className="bg-blue-900/30 text-blue-400 text-xs px-2 py-1 rounded-full">
              +{task.xpReward} XP
            </div>
            <div className="bg-emerald-900/30 text-emerald-400 text-xs px-2 py-1 rounded-full">
              +{task.reward} Token
            </div>
            <div className="bg-purple-900/30 text-purple-400 text-xs px-2 py-1 rounded-full">
              {task.taskType === 'follow' ? 'Takip' : task.taskType === 'message' ? 'Mesaj' : task.taskType === 'watch' ? 'İzleme' : 'Diğer'}
            </div>
          </div>
          
          {successMessage && (
            <div className="mb-3 p-2 bg-emerald-900/20 border border-emerald-700/30 text-emerald-400 text-sm rounded-lg">
              ✅ {successMessage}
            </div>
          )}
          
          {error && !loading && (
            <div className="mb-3 p-2 bg-red-900/20 border border-red-700/30 text-red-400 text-sm rounded-lg">
              ❌ {error}
            </div>
          )}
          
          <button
            className={`w-full py-2 px-4 rounded-lg font-medium text-white ${
              taskCompleted 
                ? 'bg-gray-700 cursor-not-allowed' 
                : completing 
                  ? 'bg-amber-600 cursor-wait'
                  : 'bg-gradient-to-r from-pink-500 to-purple-600 hover:opacity-90'
            }`}
            onClick={handleCompleteTask}
            disabled={taskCompleted || completing}
          >
            {taskCompleted 
              ? '✓ Tamamlandı' 
              : completing 
                ? 'İşleniyor...' 
                : 'Görevi Tamamla'}
          </button>
        </div>
      )}
      
      {loading ? (
        <div className="flex justify-center items-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-pink-500"></div>
        </div>
      ) : (
        <>
          {showCompletions.length > 0 ? (
            <div className="space-y-3">
              {showCompletions.map((user) => (
                <div key={user.id} className="flex items-center justify-between bg-black/20 p-3 rounded-lg">
                  <div className="flex items-center">
                    <img 
                      src={user.avatar} 
                      alt={user.username} 
                      className="w-10 h-10 rounded-full mr-3"
                    />
                    <div>
                      <div className="font-medium">{user.username}</div>
                      <div className="text-xs text-gray-400">
                        {getTimeAgo(user.completedAt)}
                      </div>
                    </div>
                  </div>
                  
                  {task && (
                    <div className="text-right">
                      <div className="text-emerald-400 font-medium">+{task.reward} Token</div>
                      <div className="text-xs text-blue-400">+{task.xpReward} XP</div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-6 text-gray-500">
              Henüz görevi tamamlayan kullanıcı bulunmuyor.
            </div>
          )}
          
          <div className="mt-4 pt-4 border-t border-gray-800">
            <div className="flex justify-between text-sm">
              <div>
                <span className="text-gray-400">Mevcut XP:</span> 
                <span className="ml-1 text-blue-400 font-medium">{xp}</span>
              </div>
              <div>
                <span className="text-gray-400">Token:</span> 
                <span className="ml-1 text-emerald-400 font-medium">{tokens}</span>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default TaskCompletions; 