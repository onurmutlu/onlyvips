import React from 'react';
import { NavLink } from 'react-router-dom';

const Navigation = () => {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-10 bg-bg-card border-t border-border-color pb-safe">
      <div className="flex justify-between items-center px-4 py-2">
        <NavLink 
          to="/" 
          end
          className={({ isActive }) => 
            `flex flex-col items-center p-2 ${isActive ? 'text-primary' : 'text-text-muted'}`
          }
        >
          <div className="i-mdi-home text-xl"></div>
          <span className="text-xs mt-1">Ana Sayfa</span>
        </NavLink>
        
        <NavLink 
          to="/content" 
          className={({ isActive }) => 
            `flex flex-col items-center p-2 ${isActive ? 'text-primary' : 'text-text-muted'}`
          }
        >
          <div className="i-mdi-movie text-xl"></div>
          <span className="text-xs mt-1">İçerikler</span>
        </NavLink>
        
        <NavLink 
          to="/packages" 
          className={({ isActive }) => 
            `flex flex-col items-center p-2 ${isActive ? 'text-primary' : 'text-text-muted'}`
          }
        >
          <div className="i-mdi-gift text-xl"></div>
          <span className="text-xs mt-1">VIP Paketler</span>
        </NavLink>
        
        <NavLink 
          to="/stats" 
          className={({ isActive }) => 
            `flex flex-col items-center p-2 ${isActive ? 'text-primary' : 'text-text-muted'}`
          }
        >
          <div className="i-mdi-chart-line text-xl"></div>
          <span className="text-xs mt-1">İstatistik</span>
        </NavLink>
        
        <NavLink 
          to="/profile" 
          className={({ isActive }) => 
            `flex flex-col items-center p-2 ${isActive ? 'text-primary' : 'text-text-muted'}`
          }
        >
          <div className="i-mdi-account text-xl"></div>
          <span className="text-xs mt-1">Profil</span>
        </NavLink>
      </div>
    </nav>
  );
};

export default Navigation; 