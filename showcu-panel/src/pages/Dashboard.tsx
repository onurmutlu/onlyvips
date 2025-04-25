import React, { useEffect } from 'react';
import { Card, Statistic, Row, Col, Spin } from 'antd';
import { useAnalytics } from '../hooks/useAnalytics';
import { useContent } from '../hooks/useContent';
import { usePackages } from '../hooks/usePackages';
import { useSubscribers } from '../hooks/useSubscribers';
import { formatCurrency } from '../utils/format';

const Dashboard: React.FC = () => {
  const { analytics, loading: analyticsLoading, error: analyticsError, fetchOverview } = useAnalytics();
  const { contents, loading: contentsLoading } = useContent();
  const { packages, loading: packagesLoading } = usePackages();
  const { subscribers, loading: subscribersLoading } = useSubscribers();

  useEffect(() => {
    fetchOverview();
  }, []);

  const loading = analyticsLoading || contentsLoading || packagesLoading || subscribersLoading;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Spin size="large" />
      </div>
    );
  }

  if (analyticsError) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Card className="w-full max-w-md">
          <div className="text-red-500 text-center">{analyticsError}</div>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">Dashboard</h1>
        <p className="text-gray-500">Hesabınızın genel durumunu görüntüleyin</p>
      </div>

      <Row gutter={[16, 16]} className="mb-6">
        <Col xs={24} sm={12} md={6}>
          <Card className="h-full">
            <Statistic
              title="Toplam İçerik"
              value={contents.length}
              valueStyle={{ color: '#1677ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="h-full">
            <Statistic
              title="VIP Paketler"
              value={packages.length}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="h-full">
            <Statistic
              title="Toplam Abone"
              value={subscribers.length}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="h-full">
            <Statistic
              title="Toplam Gelir"
              value={formatCurrency(analytics?.totalRevenue || 0)}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="Son Eklenen İçerikler">
            <div className="space-y-4">
              {contents.slice(0, 5).map((content) => (
                <div key={content.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <h3 className="font-medium">{content.title}</h3>
                    <p className="text-gray-500 text-sm">{content.mediaType}</p>
                  </div>
                  <span className={`px-2 py-1 rounded ${
                    content.isPremium ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'
                  }`}>
                    {content.isPremium ? 'Premium' : 'Ücretsiz'}
                  </span>
                </div>
              ))}
            </div>
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="Son Aboneler">
            <div className="space-y-4">
              {subscribers.slice(0, 5).map((subscriber) => (
                <div key={subscriber.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <h3 className="font-medium">{subscriber.username}</h3>
                    <p className="text-gray-500 text-sm">{subscriber.packageName}</p>
                  </div>
                  <span className={`px-2 py-1 rounded ${
                    subscriber.status === 'active' ? 'bg-green-100 text-green-800' :
                    subscriber.status === 'expired' ? 'bg-red-100 text-red-800' :
                    'bg-orange-100 text-orange-800'
                  }`}>
                    {subscriber.status === 'active' ? 'Aktif' :
                     subscriber.status === 'expired' ? 'Süresi Dolmuş' :
                     'İptal Edilmiş'}
                  </span>
                </div>
              ))}
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard; 