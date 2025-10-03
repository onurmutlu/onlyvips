import React, { useState, useEffect } from 'react';
import { useUserStore } from '../stores/userStore';

interface XPProgressBarProps {
  showAnimation?: boolean;
  gainedXP?: number;
}

const XPProgressBar: React.FC<XPProgressBarProps> = ({ 
  showAnimation = false, 
  gainedXP = 0 
}) => {
  const { xp, level, nextLevelProgress } = useUserStore();
  
  const [animatedXP, setAnimatedXP] = useState(0);
  const [animatedProgress, setAnimatedProgress] = useState(0);
  const [showLevelUp, setShowLevelUp] = useState(false);
  const [oldLevel, setOldLevel] = useState(level);
  
  // İlerlemeyi hesapla
  const progress = nextLevelProgress ? nextLevelProgress().percentage : 0;
  
  useEffect(() => {
    // Eğer animasyon gösterilmeyecekse, doğrudan mevcut değerleri kullan
    if (!showAnimation) {
      setAnimatedProgress(progress);
      setAnimatedXP(xp);
      return;
    }
    
    // XP kazanıldığında animasyon göster
    if (gainedXP > 0) {
      const startXP = xp - gainedXP;
      const startProgress = Math.floor((startXP % 100) / 100 * 100);
      
      // Eski seviyeyi kaydet
      setOldLevel(Math.floor(startXP / 100) + 1);
      
      // Başlangıç değerlerini ayarla
      setAnimatedXP(startXP);
      setAnimatedProgress(startProgress);
      
      // XP animasyonu
      const xpInterval = setInterval(() => {
        setAnimatedXP(prev => {
          // Tüm XP gösterildi mi?
          if (prev >= xp) {
            clearInterval(xpInterval);
            return xp;
          }
          return prev + 1;
        });
      }, 20);
      
      // İlerleme çubuğu animasyonu (XP'den bağımsız olarak daha yavaş ilerlesin)
      const progressInterval = setInterval(() => {
        setAnimatedProgress(prev => {
          // Eğer yeni seviyeye geçildiyse önce 100% göster
          if (level > oldLevel && prev < 100) {
            return Math.min(prev + 2, 100);
          } 
          // Seviye atlandıysa ve 100%'e ulaşıldıysa, seviye atlama efektini göster
          else if (level > oldLevel && prev >= 100) {
            clearInterval(progressInterval);
            
            // Seviye atlama animasyonu
            setShowLevelUp(true);
            setTimeout(() => {
              // 1.5 saniye sonra sıfırdan başla
              setAnimatedProgress(0);
              
              // Kalan ilerlemeyi göster
              setTimeout(() => {
                const remainingProgress = progress;
                
                // Yeni ilerlemeyi animasyonla göster
                const newProgressInterval = setInterval(() => {
                  setAnimatedProgress(p => {
                    if (p >= remainingProgress) {
                      clearInterval(newProgressInterval);
                      return remainingProgress;
                    }
                    return p + 1;
                  });
                }, 10);
              }, 500);
              
            }, 1500);
            
            return 100;
          } 
          // Normal ilerleme
          else {
            // Hedef ilerlemeye ulaşıldı mı?
            if (prev >= progress) {
              clearInterval(progressInterval);
              return progress;
            }
            return prev + 1;
          }
        });
      }, 15);
      
      return () => {
        clearInterval(xpInterval);
        clearInterval(progressInterval);
      };
    } else {
      // XP kazanımı yok, normal değerleri göster
      setAnimatedProgress(progress);
      setAnimatedXP(xp);
    }
  }, [showAnimation, gainedXP, xp, progress, level, oldLevel, nextLevelProgress]);
  
  return (
    <div className="w-full">
      <div className="flex justify-between text-xs mb-1">
        <div className="text-blue-400">
          <span className="font-medium">
            {showAnimation ? animatedXP : xp}
          </span> XP
          
          {/* XP Kazanımı göstergesi */}
          {showAnimation && gainedXP > 0 && (
            <span className="ml-1 text-emerald-400 animate-pulse">
              +{gainedXP}
            </span>
          )}
        </div>
        
        <div className="text-purple-400">
          Level <span className="font-medium">{level}</span>
        </div>
      </div>
      
      {/* XP İlerleme Çubuğu */}
      <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
        <div 
          className={`h-full bg-gradient-to-r from-blue-500 to-purple-500 ${showAnimation ? 'transition-all duration-300 ease-out' : ''}`}
          style={{ width: `${showAnimation ? animatedProgress : progress}%` }}
        ></div>
      </div>
      
      {/* Seviye Atlama Efekti */}
      {showLevelUp && (
        <div className="relative">
          <div className="absolute top-0 left-0 right-0 -mt-2 animate-levelup">
            <div className="px-4 py-2 bg-purple-600/80 text-white rounded-lg text-center font-bold text-sm shadow-lg border border-purple-400">
              🎉 Tebrikler! Seviye {oldLevel} → {level}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default XPProgressBar; 