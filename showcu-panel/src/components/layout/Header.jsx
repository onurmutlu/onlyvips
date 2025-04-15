import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTelegramContext } from '../../TelegramProvider';

const Header = ({ title }) => {
  const { tg } = useTelegramContext();
  const navigate = useNavigate();
  
  const handleBackClick = () => {
    navigate(-1);
  };
  
  return (
    <header className="sticky top-0 z-10 backdrop-blur bg-bg-main bg-opacity-80 border-b border-border-color">
      <div className="flex items-center justify-between px-4 py-3">
        <div className="flex items-center">
          {/* Eğer ana sayfa değilse geri butonu göster */}
          {title !== 'Şovcu Paneli' && (
            <button 
              onClick={handleBackClick}
              className="mr-3 text-text-muted hover:text-text-light"
            >
              <div className="i-mdi-arrow-left text-xl"></div>
            </button>
          )}
          
          <h1 className="text-lg font-semibold">{title}</h1>
        </div>
        
        <div className="flex items-center">
          {/* Bildirim ikonu */}
          <button className="relative p-2 text-text-muted hover:text-text-light">
            <div className="i-mdi-bell text-xl"></div>
            <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-primary"></span>
          </button>
          
          {/* Arama ikonu */}
          <button className="p-2 ml-1 text-text-muted hover:text-text-light">
            <div className="i-mdi-magnify text-xl"></div>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header; 