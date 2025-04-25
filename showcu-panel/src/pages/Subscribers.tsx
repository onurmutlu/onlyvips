import React, { useEffect, useState } from 'react';
import { Card, Table, Tag, Button, Input, message, Spin } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { useSubscribers } from '../hooks/useSubscribers';
import { formatCurrency } from '../utils/format';
import dayjs from 'dayjs';

const { Search } = Input;

const Subscribers: React.FC = () => {
  const { subscribers, loading, error, fetchSubscribers } = useSubscribers();
  const [searchText, setSearchText] = useState('');

  useEffect(() => {
    fetchSubscribers();
  }, []);

  const filteredSubscribers = subscribers.filter(subscriber =>
    subscriber.username.toLowerCase().includes(searchText.toLowerCase()) ||
    subscriber.packageName.toLowerCase().includes(searchText.toLowerCase())
  );

  const columns = [
    {
      title: 'Kullanıcı',
      dataIndex: 'username',
      key: 'username',
      render: (text: string) => <span className="font-medium">{text}</span>,
    },
    {
      title: 'Paket',
      dataIndex: 'packageName',
      key: 'packageName',
    },
    {
      title: 'Başlangıç',
      dataIndex: 'startDate',
      key: 'startDate',
      render: (date: string) => dayjs(date).format('DD MMM YYYY'),
    },
    {
      title: 'Bitiş',
      dataIndex: 'endDate',
      key: 'endDate',
      render: (date: string) => dayjs(date).format('DD MMM YYYY'),
    },
    {
      title: 'Durum',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const statusConfig = {
          active: { color: 'green', text: 'Aktif' },
          expired: { color: 'red', text: 'Süresi Dolmuş' },
          cancelled: { color: 'orange', text: 'İptal Edilmiş' },
        };
        const config = statusConfig[status as keyof typeof statusConfig];
        return (
          <Tag color={config.color}>
            {config.text}
          </Tag>
        );
      },
    },
  ];

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

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">Abonelerim</h1>
        <p className="text-gray-500">VIP abonelerinizi görüntüleyin ve yönetin</p>
      </div>

      <div className="mb-6">
        <Search
          placeholder="Abone ara..."
          allowClear
          enterButton={<SearchOutlined />}
          size="large"
          onChange={(e) => setSearchText(e.target.value)}
          className="max-w-md"
        />
      </div>

      <Card>
        <Table
          columns={columns}
          dataSource={filteredSubscribers}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `Toplam ${total} abone`,
          }}
        />
      </Card>
    </div>
  );
};

export default Subscribers; 