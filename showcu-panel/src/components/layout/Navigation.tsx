import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { HomeOutlined, AppstoreOutlined, WalletOutlined, UserOutlined } from '@ant-design/icons';

const Navigation: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const items = [
    {
      key: '/dashboard',
      icon: <HomeOutlined />,
      label: 'Dashboard',
    },
    {
      key: '/content',
      icon: <AppstoreOutlined />,
      label: 'İçerikler',
    },
    {
      key: '/wallet',
      icon: <WalletOutlined />,
      label: 'Cüzdan',
    },
    {
      key: '/profile',
      icon: <UserOutlined />,
      label: 'Profil',
    },
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-gray-900/80 backdrop-blur-lg border-t border-white/10">
      <div className="container mx-auto">
        <div className="flex justify-around py-3">
          {items.map((item) => (
            <button
              key={item.key}
              onClick={() => navigate(item.key)}
              className={`flex flex-col items-center space-y-1 px-4 py-2 rounded-lg transition-all ${
                location.pathname === item.key
                  ? 'text-purple-400 bg-white/5'
                  : 'text-white/60 hover:text-white/80'
              }`}
            >
              {item.icon}
              <span className="text-xs">{item.label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Navigation; 