import React from 'react';
import { Card, Statistic, Table, Tag, Space } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined, EyeOutlined, DollarOutlined, UserOutlined } from '@ant-design/icons';
import Navigation from '../components/layout/Navigation';

const Dashboard: React.FC = () => {
  const stats = [
    {
      title: 'Toplam İzlenme',
      value: 1250,
      change: 12.5,
      icon: <EyeOutlined className="text-purple-400" />,
    },
    {
      title: 'Toplam Gelir',
      value: 2500,
      change: 8.2,
      icon: <DollarOutlined className="text-green-400" />,
    },
    {
      title: 'Aktif Abone',
      value: 45,
      change: -2.1,
      icon: <UserOutlined className="text-blue-400" />,
    },
  ];

  const recentContent = [
    {
      key: '1',
      title: 'Özel İçerik #1',
      views: 128,
      revenue: 12.5,
      status: 'published',
    },
    {
      key: '2',
      title: 'Özel İçerik #2',
      views: 95,
      revenue: 8.2,
      status: 'published',
    },
  ];

  const columns = [
    {
      title: 'İçerik',
      dataIndex: 'title',
      key: 'title',
      render: (text: string) => <span className="text-white font-medium">{text}</span>,
    },
    {
      title: 'İzlenme',
      dataIndex: 'views',
      key: 'views',
      render: (views: number) => <span className="text-white/70">{views}</span>,
    },
    {
      title: 'Gelir',
      dataIndex: 'revenue',
      key: 'revenue',
      render: (revenue: number) => <span className="text-green-400">{revenue} TON</span>,
    },
    {
      title: 'Durum',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'published' ? 'green' : 'orange'}>
          {status === 'published' ? 'Yayında' : 'Taslak'}
        </Tag>
      ),
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-indigo-900 text-white">
      <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))]"></div>
      
      <div className="container mx-auto px-4 py-8 relative z-10">
        <h1 className="text-2xl font-bold mb-6">Dashboard</h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {stats.map((stat, index) => (
            <Card key={index} className="bg-white/5 backdrop-blur-lg border-0 shadow-xl">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-white/60 mb-2">{stat.title}</p>
                  <Statistic
                    value={stat.value}
                    valueStyle={{ color: '#fff' }}
                    className="text-2xl font-bold"
                  />
                </div>
                <div className="text-3xl">{stat.icon}</div>
              </div>
              <div className="mt-4 flex items-center">
                {stat.change > 0 ? (
                  <ArrowUpOutlined className="text-green-400 mr-1" />
                ) : (
                  <ArrowDownOutlined className="text-red-400 mr-1" />
                )}
                <span className={stat.change > 0 ? 'text-green-400' : 'text-red-400'}>
                  {Math.abs(stat.change)}%
                </span>
                <span className="text-white/60 ml-2">geçen aya göre</span>
              </div>
            </Card>
          ))}
        </div>

        <Card className="bg-white/5 backdrop-blur-lg border-0 shadow-xl">
          <h2 className="text-xl font-bold mb-4">Son İçerikler</h2>
          <Table
            columns={columns}
            dataSource={recentContent}
            pagination={false}
            className="[&_.ant-table-thead>tr>th]:bg-transparent [&_.ant-table-thead>tr>th]:text-white/60 [&_.ant-table-tbody>tr>td]:bg-transparent [&_.ant-table-tbody>tr:hover>td]:bg-white/5"
          />
        </Card>
      </div>

      <Navigation />
    </div>
  );
};

export default Dashboard; 