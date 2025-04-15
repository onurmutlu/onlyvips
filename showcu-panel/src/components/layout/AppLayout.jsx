import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { useTelegramContext } from '../../TelegramProvider';
import Header from './Header';
import Navigation from './Navigation';

const AppLayout = () => {
  const { tg } = useTelegramContext();
  const location = useLocation();
  const navigate = useNavigate();
  const [title, setTitle] = useState('Şovcu Paneli');
  
  useEffect(() => {
    // Sayfa değişikliklerinde Telegram back butonunu yapılandır
    if (tg?.BackButton) {
      if (location.pathname === '/') {
        tg.BackButton.hide();
      } else {
        tg.BackButton.show();
        
        const handleBackButton = () => {
          navigate(-1);
        };
        
        tg.onEvent('backButtonClicked', handleBackButton);
        
        return () => {
          tg.offEvent('backButtonClicked', handleBackButton);
        };
      }
    }
    
    // Sayfa başlıklarını güncelle
    switch (location.pathname) {
      case '/':
        setTitle('Şovcu Paneli');
        break;
      case '/content':
        setTitle('İçerik Yönetimi');
        break;
      case '/packages':
        setTitle('VIP Paketler');
        break;
      case '/stats':
        setTitle('İstatistikler');
        break;
      case '/profile':
        setTitle('Profil');
        break;
      default:
        if (location.pathname.startsWith('/content/')) {
          setTitle('İçerik Detayı');
        } else if (location.pathname.startsWith('/packages/')) {
          setTitle('Paket Detayı');
        } else {
          setTitle('Şovcu Paneli');
        }
    }
  }, [location, navigate, tg]);
  
  return (
    <div className="min-h-screen bg-bg-main flex flex-col">
      <Header title={title} />
      
      <main className="flex-1 px-4 py-6">
        <Outlet />
      </main>
      
      <Navigation />
    </div>
  );
};

export default AppLayout; 