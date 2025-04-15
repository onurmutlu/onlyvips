import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getDashboardStats } from '../api/stats';
import { useTelegramContext } from '../TelegramProvider';

// Bileşenler
import StatsCard from '../components/dashboard/StatsCard';
import RevenueChart from '../components/dashboard/RevenueChart';
import TopContents from '../components/dashboard/TopContents';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { user } = useTelegramContext();
  
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await getDashboardStats();
        setStats(data);
        setError(null);
      } catch (err) {
        console.error('İstatistik hatası:', err);
        setError('İstatistikler yüklenemedi');
      } finally {
        setLoading(false);
      }
    };
    
    fetchStats();
  }, []);
  
  if (loading) {
    return (
      <div className="flex justify-center items-center h-[60vh]">
        <div className="loading-spinner"></div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="card p-6 text-center">
        <div className="i-mdi-alert-circle text-4xl text-error mx-auto mb-3"></div>
        <h2 className="text-xl font-medium mb-2">Bir Hata Oluştu</h2>
        <p className="text-text-muted mb-4">{error}</p>
        <button 
          onClick={() => window.location.reload()}
          className="btn-primary"
        >
          Tekrar Dene
        </button>
      </div>
    );
  }
  
  return (
    <div className="pb-16">
      {/* Karşılama Başlığı */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-1">
          Merhaba, <span className="gradient-text">{user?.first_name || 'Şovcu'}</span>!
        </h1>
        <p className="text-text-muted">
          Bugünkü kazanç ve performans özetiniz
        </p>
      </div>
      
      {/* Ana İstatistik Kartları */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <StatsCard 
          title="Toplam Kazanç"
          value={`${stats.total_revenue} TON`}
          icon="cash-multiple"
          trend={stats.revenue_trend}
          color="primary"
        />
        
        <StatsCard 
          title="Görüntülenmeler"
          value={stats.total_views}
          icon="eye"
          trend={stats.views_trend}
          color="info"
        />
        
        <StatsCard 
          title="Aktif Aboneler"
          value={stats.active_subscribers}
          icon="account-check"
          trend={stats.subscribers_trend}
          color="success"
        />
        
        <StatsCard 
          title="İçerikler"
          value={stats.content_count}
          icon="movie"
          trend={stats.content_trend}
          color="accent"
        />
      </div>
      
      {/* Gelir Grafiği */}
      <div className="card mb-6">
        <div className="flex justify-between items-center p-4 border-b border-border-color">
          <h2 className="text-lg font-semibold">Gelir Grafiği</h2>
          <Link to="/stats" className="text-primary text-sm">
            Detaylı İstatistikler
          </Link>
        </div>
        <div className="p-4">
          <RevenueChart data={stats.revenue_chart} />
        </div>
      </div>
      
      {/* İçerik ve Abone Bilgileri */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* En Çok Kazandıran İçerikler */}
        <div className="card">
          <div className="flex justify-between items-center p-4 border-b border-border-color">
            <h2 className="text-lg font-semibold">Popüler İçerikler</h2>
            <Link to="/content" className="text-primary text-sm">
              Tüm İçerikler
            </Link>
          </div>
          <div className="p-4">
            <TopContents contents={stats.top_contents} />
          </div>
        </div>
        
        {/* Son Etkinlikler */}
        <div className="card">
          <div className="flex justify-between items-center p-4 border-b border-border-color">
            <h2 className="text-lg font-semibold">Son Satışlar</h2>
            <span className="text-xs text-text-muted">Son 24 saat</span>
          </div>
          <div className="p-4">
            {stats.recent_sales.length > 0 ? (
              <ul className="divide-y divide-border-color">
                {stats.recent_sales.map((sale, index) => (
                  <li key={index} className="py-3">
                    <div className="flex justify-between">
                      <div>
                        <p className="font-medium">{sale.title}</p>
                        <p className="text-xs text-text-muted">
                          {new Date(sale.date).toLocaleString('tr-TR')}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-success">{sale.amount} TON</p>
                        <p className="text-xs text-text-muted">{sale.user}</p>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="text-center py-6">
                <div className="i-mdi-cart-off text-4xl text-text-muted mx-auto mb-2"></div>
                <p className="text-text-muted">Henüz satış bulunmuyor</p>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Yeni İçerik ve VIP Paket Ekleme Butonları */}
      <div className="fixed bottom-20 right-4 flex flex-col space-y-2">
        <Link
          to="/content"
          className="w-12 h-12 rounded-full bg-gradient-primary flex items-center justify-center shadow-lg"
        >
          <div className="i-mdi-movie-plus text-2xl text-white"></div>
        </Link>
        <Link
          to="/packages"
          className="w-12 h-12 rounded-full bg-gradient-primary flex items-center justify-center shadow-lg"
        >
          <div className="i-mdi-package-variant-plus text-2xl text-white"></div>
        </Link>
      </div>
    </div>
  );
};

export default Dashboard; 