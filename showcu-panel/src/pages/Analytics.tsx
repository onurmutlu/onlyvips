import React, { useEffect } from 'react';
import { Card, Statistic, Row, Col, DatePicker, Spin } from 'antd';
import { Line } from 'react-chartjs-2';
import { useAnalytics } from '../hooks/useAnalytics';
import { formatCurrency } from '../utils/format';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;

const Analytics: React.FC = () => {
  const { analytics, loading, error, fetchOverview, fetchRevenue } = useAnalytics();
  const [dateRange, setDateRange] = React.useState<[dayjs.Dayjs, dayjs.Dayjs]>([
    dayjs().subtract(30, 'days'),
    dayjs(),
  ]);

  useEffect(() => {
    fetchOverview();
  }, []);

  useEffect(() => {
    if (dateRange[0] && dateRange[1]) {
      fetchRevenue(dateRange[0].format('YYYY-MM-DD'), dateRange[1].format('YYYY-MM-DD'));
    }
  }, [dateRange]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Spin size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Card className="w-full max-w-md">
          <div className="text-red-500 text-center">{error}</div>
        </Card>
      </div>
    );
  }

  const revenueChartData = {
    labels: analytics?.revenueByDate.map(item => dayjs(item.date).format('DD MMM')),
    datasets: [
      {
        label: 'Gelir',
        data: analytics?.revenueByDate.map(item => item.amount),
        borderColor: '#1677ff',
        backgroundColor: 'rgba(22, 119, 255, 0.1)',
        tension: 0.4,
      },
    ],
  };

  const subscriberChartData = {
    labels: analytics?.subscriberGrowth.map(item => dayjs(item.date).format('DD MMM')),
    datasets: [
      {
        label: 'Abone Sayısı',
        data: analytics?.subscriberGrowth.map(item => item.count),
        borderColor: '#52c41a',
        backgroundColor: 'rgba(82, 196, 26, 0.1)',
        tension: 0.4,
      },
    ],
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">Analitik</h1>
        <p className="text-gray-500">Performans metriklerinizi takip edin</p>
      </div>

      <div className="mb-6">
        <RangePicker
          value={dateRange}
          onChange={(dates) => setDateRange(dates as [dayjs.Dayjs, dayjs.Dayjs])}
          className="w-full max-w-md"
        />
      </div>

      <Row gutter={[16, 16]} className="mb-6">
        <Col xs={24} sm={12} md={8}>
          <Card className="h-full">
            <Statistic
              title="Toplam Görüntülenme"
              value={analytics?.totalViews}
              valueStyle={{ color: '#1677ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8}>
          <Card className="h-full">
            <Statistic
              title="Toplam Abone"
              value={analytics?.totalSubscribers}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8}>
          <Card className="h-full">
            <Statistic
              title="Toplam Gelir"
              value={formatCurrency(analytics?.totalRevenue || 0)}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="Gelir Analizi" className="h-full">
            <Line
              data={revenueChartData}
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    position: 'top' as const,
                  },
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    ticks: {
                      callback: (value) => formatCurrency(value as number),
                    },
                  },
                },
              }}
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Abone Büyümesi" className="h-full">
            <Line
              data={subscriberChartData}
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    position: 'top' as const,
                  },
                },
                scales: {
                  y: {
                    beginAtZero: true,
                  },
                },
              }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} className="mt-6">
        <Col xs={24}>
          <Card title="En Popüler İçerikler">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="text-left border-b">
                    <th className="p-4">İçerik</th>
                    <th className="p-4">Görüntülenme</th>
                    <th className="p-4">Gelir</th>
                  </tr>
                </thead>
                <tbody>
                  {analytics?.contentViews.map((content) => (
                    <tr key={content.id} className="border-b hover:bg-gray-50">
                      <td className="p-4">{content.title}</td>
                      <td className="p-4">{content.views}</td>
                      <td className="p-4">{formatCurrency(content.revenue)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Analytics; 