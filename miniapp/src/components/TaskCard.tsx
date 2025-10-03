import React from 'react';
import { Link } from 'react-router-dom';
import { Task, TaskType, UserTask, TaskStatus } from '../types/task';

interface TaskCardProps {
  task: Task;
  userTask?: UserTask;
  onComplete?: (taskId: string) => void;
}

const TaskCard: React.FC<TaskCardProps> = ({ task, userTask, onComplete }) => {
  const isCompleted = userTask?.status === TaskStatus.COMPLETED || 
                     userTask?.status === TaskStatus.VERIFIED;
  
  // Görev tipine göre ikon ve renk belirle
  const getTaskMeta = (type: TaskType) => {
    switch (type) {
      case TaskType.CONTENT_VIEW:
        return { icon: '👁️', color: 'text-blue-400', bgColor: 'bg-blue-900/30' };
      case TaskType.CONTENT_PURCHASE:
        return { icon: '🛒', color: 'text-green-400', bgColor: 'bg-green-900/30' };
      case TaskType.REFERRAL:
        return { icon: '👥', color: 'text-purple-400', bgColor: 'bg-purple-900/30' };
      case TaskType.SOCIAL_SHARE:
        return { icon: '🔄', color: 'text-pink-400', bgColor: 'bg-pink-900/30' };
      case TaskType.COMMENT:
        return { icon: '💬', color: 'text-yellow-400', bgColor: 'bg-yellow-900/30' };
      case TaskType.APP_USAGE:
        return { icon: '📱', color: 'text-cyan-400', bgColor: 'bg-cyan-900/30' };
      case TaskType.SUBSCRIPTION:
        return { icon: '⭐', color: 'text-amber-400', bgColor: 'bg-amber-900/30' };
      default:
        return { icon: '🎯', color: 'text-gray-400', bgColor: 'bg-gray-900/30' };
    }
  };
  
  // Toplam ödül miktarını hesapla
  const getTotalRewardsByType = (type: string) => {
    return task.rewards
      .filter(reward => reward.type === type)
      .reduce((total, reward) => total + reward.amount, 0);
  };
  
  const { icon, color, bgColor } = getTaskMeta(task.type);

  return (
    <Link 
      to={`/task/${task.id}`} 
      className={`${bgColor} border border-white/10 rounded-lg p-4 transition-transform hover:scale-[1.02] hover:shadow-lg`}
    >
      <div className="flex items-start gap-3">
        <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg ${bgColor} border border-white/10`}>
          {icon}
        </div>
        
        <div className="flex-grow">
          <div className="flex justify-between items-start">
            <h3 className="font-medium text-white">{task.title}</h3>
            {isCompleted && (
              <span className="bg-green-900/40 text-green-400 text-xs px-2 py-1 rounded-full">
                Tamamlandı
              </span>
            )}
          </div>
          
          <p className="text-gray-300 text-sm mt-1">{task.description}</p>
          
          <div className="mt-3 flex items-center justify-between">
            <div className="flex gap-2">
              {getTotalRewardsByType('token') > 0 && (
                <div className="bg-yellow-900/30 text-yellow-400 text-xs px-2 py-1 rounded-full flex items-center gap-1">
                  <span>💎</span>
                  <span>{getTotalRewardsByType('token')}</span>
                </div>
              )}
              
              {getTotalRewardsByType('xp') > 0 && (
                <div className="bg-blue-900/30 text-blue-400 text-xs px-2 py-1 rounded-full flex items-center gap-1">
                  <span>⚡</span>
                  <span>{getTotalRewardsByType('xp')} XP</span>
                </div>
              )}
              
              {task.rewards.some(reward => reward.type === 'badge') && (
                <div className="bg-purple-900/30 text-purple-400 text-xs px-2 py-1 rounded-full flex items-center gap-1">
                  <span>🏆</span>
                  <span>Rozet</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
};

export default TaskCard; 