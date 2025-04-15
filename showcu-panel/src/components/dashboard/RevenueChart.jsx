import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

// Chart.js bileşenlerini kaydet
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  Filler
);

const RevenueChart = ({ data }) => {
  // Veri yoksa veya boşsa, bir mesaj göster
  if (!data || !data.labels || data.labels.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-10">
        <div className="i-mdi-chart-line text-5xl text-text-muted mb-3"></div>
        <p className="text-text-muted">Gelir verisi bulunmuyor</p>
      </div>
    );
  }

  // Grafik verilerini hazırla
  const chartData = {
    labels: data.labels,
    datasets: [
      {
        label: 'Gelir (TON)',
        data: data.values,
        borderColor: '#FF2E93',
        backgroundColor: (context) => {
          const ctx = context.chart.ctx;
          const gradient = ctx.createLinearGradient(0, 0, 0, 200);
          gradient.addColorStop(0, 'rgba(255, 46, 147, 0.4)');
          gradient.addColorStop(1, 'rgba(255, 46, 147, 0)');
          return gradient;
        },
        borderWidth: 2,
        tension: 0.4,
        fill: true,
        pointBackgroundColor: '#FF2E93',
        pointBorderColor: '#FFFFFF',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6,
      },
    ],
  };

  // Grafik opsiyonları
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'rgba(45, 13, 49, 0.9)',
        titleColor: '#FFFFFF',
        bodyColor: '#FFFFFF',
        borderColor: 'rgba(255, 46, 147, 0.3)',
        borderWidth: 1,
        padding: 12,
        cornerRadius: 8,
        titleFont: {
          size: 14,
          weight: 'bold',
        },
        bodyFont: {
          size: 13,
        },
        callbacks: {
          label: (context) => `${context.parsed.y} TON`,
        },
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
          drawBorder: false,
        },
        ticks: {
          color: '#D3A7C7',
          font: {
            size: 11,
          },
        },
      },
      y: {
        grid: {
          color: 'rgba(255, 255, 255, 0.05)',
          drawBorder: false,
        },
        ticks: {
          color: '#D3A7C7',
          font: {
            size: 11,
          },
          callback: (value) => `${value} TON`,
        },
        beginAtZero: true,
      },
    },
  };

  return (
    <div className="h-72">
      <Line data={chartData} options={options} />
    </div>
  );
};

export default RevenueChart; 