import React, { useEffect, useState } from 'react';
import { useUserStore } from '../stores/userStore';
import { useTaskStore } from '../stores/taskStore';
import XPProgressBar from './XPProgressBar';

const StatusBar: React.FC = () => {
  // UserStore'dan XP ve token bilgilerini al
  const { tokens, showXpAnimation, lastXpGain, leveledUp } = useUserStore();
  
  // TaskStore'dan aktif görev bilgisini al
  const { activeTaskId, getTaskById } = useTaskStore();
  const activeTask = activeTaskId ? getTaskById(activeTaskId) : null;
  
  // Telegram kullanıcı bilgisini al
  const [username, setUsername] = useState<string | null>(null);
  
  useEffect(() => {
    // Telegram WebApp'inden kullanıcı adını al
    const telegramUser = window.Telegram?.WebApp?.initDataUnsafe?.user;
    if (telegramUser) {
      setUsername(telegramUser.username || 
                  `${telegramUser.first_name || ''} ${telegramUser.last_name || ''}`.trim() || 
                  'Kullanıcı');
    } else {
      setUsername('Demo Kullanıcı');
    }
  }, []);
  
  return (
    <div className="fixed top-0 left-0 right-0 bg-gray-900/90 backdrop-blur-md border-b border-gray-800 z-50 p-3 shadow-lg">
      <div className="container mx-auto flex justify-between items-center">
        {/* Kullanıcı bilgileri */}
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-full bg-gradient-to-r from-pink-500 to-purple-500 flex items-center justify-center text-sm font-bold text-white">
            {username ? username.charAt(0).toUpperCase() : '?'}
          </div>
          <span className="text-white text-sm font-medium">{username}</span>
        </div>
        
        {/* XP ve Level bilgileri (XPProgressBar bileşeni ile) */}
        <div className="flex-1 mx-8">
          <XPProgressBar 
            showAnimation={showXpAnimation} 
            gainedXP={lastXpGain} 
          />
        </div>
        
        {/* Token Bilgisi */}
        <div className="flex items-center">
          <div className="flex items-center bg-yellow-800/30 px-3 py-1 rounded-full">
            <span className="text-yellow-500 mr-1 text-xl">★</span>
            <span className="text-white font-medium">{tokens}</span>
          </div>
        </div>
      </div>
      
      {/* Aktif Görev Bildirimi */}
      {activeTask && (
        <div className="mt-2 px-3 py-2 bg-blue-900/30 border border-blue-800/50 rounded-lg text-xs animate-pulse">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-blue-400 font-medium">Aktif Görev:</span> {activeTask.title}
            </div>
            <div className="text-yellow-400">
              +{activeTask.reward} <span className="text-xs">Token</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StatusBar; 