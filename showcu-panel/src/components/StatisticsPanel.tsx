import React, { useEffect, useState } from 'react';
import api from '../api/creatorApi';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Title } from 'chart.js';
import { Pie, Line } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Title);

interface StatisticsPanelProps {
  creatorId: string;
}

interface Statistics {
  totalViews: number;
  totalLikes: number;
  totalComments: number;
  totalSubscribers: number;
  totalEarnings: number;
  monthlyEarnings: number[];
  contentPerformance: {
    contentId: string;
    title: string;
    views: number;
    likes: number;
    comments: number;
  }[];
  subscribersByPackage: {
    packageId: string;
    packageName: string;
    count: number;
  }[];
}

const StatisticsPanel: React.FC<StatisticsPanelProps> = ({ creatorId }) => {
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [timePeriod, setTimePeriod] = useState<'week' | 'month' | 'year'>('month');
  
  useEffect(() => {
    const loadStatistics = async () => {
      try {
        setLoading(true);
        const response = await api.getStatistics(timePeriod);
        
        if (response.success) {
          setStatistics(response.data);
        }
      } catch (error) {
        console.error('İstatistik yükleme hatası:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadStatistics();
  }, [creatorId, timePeriod]);
  
  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-xl text-pink-500 animate-pulse">İstatistikler yükleniyor...</div>
      </div>
    );
  }
  
  if (!statistics) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <p className="text-white">İstatistikler yüklenirken bir hata oluştu.</p>
      </div>
    );
  }
  
  // Paket abonelikleri için pasta grafik verisi
  const subscriberChartData = {
    labels: statistics.subscribersByPackage.map(item => item.packageName),
    datasets: [
      {
        label: 'Aboneler',
        data: statistics.subscribersByPackage.map(item => item.count),
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(153, 102, 255, 0.6)',
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };
  
  // Aylık kazanç için çizgi grafik verisi
  const earningsChartData = {
    labels: ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'].slice(0, statistics.monthlyEarnings.length),
    datasets: [
      {
        label: 'Aylık Kazanç (Star)',
        data: statistics.monthlyEarnings,
        fill: true,
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        borderColor: 'rgba(255, 99, 132, 1)',
        tension: 0.4,
      },
    ],
  };
  
  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h2 className="text-2xl font-bold text-white mb-6">İstatistikler ve Performans</h2>
      
      {/* Zaman aralığı seçici */}
      <div className="flex gap-4 mb-6">
        <button 
          className={`px-4 py-2 rounded-lg ${timePeriod === 'week' ? 'bg-pink-500 text-white' : 'bg-gray-700 text-gray-300'}`}
          onClick={() => setTimePeriod('week')}
        >
          Haftalık
        </button>
        <button 
          className={`px-4 py-2 rounded-lg ${timePeriod === 'month' ? 'bg-pink-500 text-white' : 'bg-gray-700 text-gray-300'}`}
          onClick={() => setTimePeriod('month')}
        >
          Aylık
        </button>
        <button 
          className={`px-4 py-2 rounded-lg ${timePeriod === 'year' ? 'bg-pink-500 text-white' : 'bg-gray-700 text-gray-300'}`}
          onClick={() => setTimePeriod('year')}
        >
          Yıllık
        </button>
      </div>
      
      {/* Özet bilgiler */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
        <div className="bg-gray-700 p-4 rounded-lg">
          <p className="text-gray-400 text-sm">Toplam Görüntülenme</p>
          <p className="text-2xl font-bold text-white">{statistics.totalViews}</p>
        </div>
        <div className="bg-gray-700 p-4 rounded-lg">
          <p className="text-gray-400 text-sm">Toplam Beğeni</p>
          <p className="text-2xl font-bold text-white">{statistics.totalLikes}</p>
        </div>
        <div className="bg-gray-700 p-4 rounded-lg">
          <p className="text-gray-400 text-sm">Toplam Yorum</p>
          <p className="text-2xl font-bold text-white">{statistics.totalComments}</p>
        </div>
        <div className="bg-gray-700 p-4 rounded-lg">
          <p className="text-gray-400 text-sm">Toplam Abone</p>
          <p className="text-2xl font-bold text-white">{statistics.totalSubscribers}</p>
        </div>
        <div className="bg-pink-700 p-4 rounded-lg">
          <p className="text-pink-200 text-sm">Toplam Kazanç</p>
          <p className="text-2xl font-bold text-white">{statistics.totalEarnings} Star</p>
        </div>
      </div>
      
      {/* Grafikler */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        <div>
          <h3 className="text-white text-lg font-semibold mb-4">Abonelik Dağılımı</h3>
          <div className="bg-gray-700 p-4 rounded-lg">
            <Pie data={subscriberChartData} />
          </div>
        </div>
        <div>
          <h3 className="text-white text-lg font-semibold mb-4">Aylık Kazanç</h3>
          <div className="bg-gray-700 p-4 rounded-lg">
            <Line 
              data={earningsChartData} 
              options={{
                scales: {
                  y: {
                    beginAtZero: true,
                    ticks: {
                      color: 'rgba(255, 255, 255, 0.7)'
                    },
                    grid: {
                      color: 'rgba(255, 255, 255, 0.1)'
                    }
                  },
                  x: {
                    ticks: {
                      color: 'rgba(255, 255, 255, 0.7)'
                    },
                    grid: {
                      color: 'rgba(255, 255, 255, 0.1)'
                    }
                  }
                }
              }}
            />
          </div>
        </div>
      </div>
      
      {/* İçerik Performans Tablosu */}
      <div className="mt-8">
        <h3 className="text-white text-lg font-semibold mb-4">İçerik Performansı</h3>
        <div className="bg-gray-700 rounded-lg overflow-hidden">
          <table className="w-full text-left">
            <thead className="bg-gray-800">
              <tr>
                <th className="p-3 text-white">İçerik</th>
                <th className="p-3 text-white">Görüntülenme</th>
                <th className="p-3 text-white">Beğeni</th>
                <th className="p-3 text-white">Yorum</th>
                <th className="p-3 text-white">Etkileşim Oranı</th>
              </tr>
            </thead>
            <tbody>
              {statistics.contentPerformance.map(content => (
                <tr key={content.contentId} className="border-t border-gray-600">
                  <td className="p-3 text-white">{content.title}</td>
                  <td className="p-3 text-white">{content.views}</td>
                  <td className="p-3 text-white">{content.likes}</td>
                  <td className="p-3 text-white">{content.comments}</td>
                  <td className="p-3 text-white">
                    {content.views > 0 
                      ? `${(((content.likes + content.comments) / content.views) * 100).toFixed(1)}%` 
                      : '0%'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default StatisticsPanel;