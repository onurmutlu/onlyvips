import React, { useState } from 'react';
import { Card, Button, Table, Tag, Space, Modal, Form, Input, InputNumber } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import Navigation from '../components/layout/Navigation';

const Packages: React.FC = () => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [form] = Form.useForm();

  const columns = [
    {
      title: 'Paket Adı',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => <span className="text-white font-medium">{text}</span>,
    },
    {
      title: 'Fiyat',
      dataIndex: 'price',
      key: 'price',
      render: (price: number) => <span className="text-green-400">{price} TON</span>,
    },
    {
      title: 'Süre',
      dataIndex: 'duration',
      key: 'duration',
      render: (duration: number) => <span className="text-white/70">{duration} gün</span>,
    },
    {
      title: 'Abone',
      dataIndex: 'subscribers',
      key: 'subscribers',
      render: (subscribers: number) => <span className="text-white/70">{subscribers}</span>,
    },
    {
      title: 'Durum',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'active' ? 'green' : 'red'}>
          {status === 'active' ? 'Aktif' : 'Pasif'}
        </Tag>
      ),
    },
    {
      title: 'İşlemler',
      key: 'action',
      render: () => (
        <Space size="middle">
          <Button type="text" icon={<EditOutlined className="text-purple-400" />} />
          <Button type="text" icon={<DeleteOutlined className="text-red-400" />} />
        </Space>
      ),
    },
  ];

  const data = [
    {
      key: '1',
      name: 'VIP Paket',
      price: 100,
      duration: 30,
      subscribers: 12,
      status: 'active',
    },
    {
      key: '2',
      name: 'Premium Paket',
      price: 50,
      duration: 15,
      subscribers: 8,
      status: 'active',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-indigo-900 text-white">
      <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))]"></div>
      
      <div className="container mx-auto px-4 py-8 relative z-10">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">Paketlerim</h1>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setIsModalVisible(true)}
            className="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 border-0"
          >
            Yeni Paket
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {data.map((item) => (
            <Card
              key={item.key}
              className="bg-white/5 backdrop-blur-lg border-0 shadow-xl hover:shadow-2xl transition-all duration-300"
            >
              <div className="text-center">
                <h2 className="text-xl font-bold mb-2">{item.name}</h2>
                <div className="text-3xl font-bold text-purple-400 mb-4">{item.price} TON</div>
                <div className="space-y-2 text-white/70">
                  <div>{item.duration} gün erişim</div>
                  <div>{item.subscribers} aktif abone</div>
                </div>
                <Button
                  type="primary"
                  className="mt-6 w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 border-0"
                >
                  Düzenle
                </Button>
              </div>
            </Card>
          ))}
        </div>

        <Card className="bg-white/5 backdrop-blur-lg border-0 shadow-xl">
          <Table
            columns={columns}
            dataSource={data}
            pagination={false}
            className="[&_.ant-table-thead>tr>th]:bg-transparent [&_.ant-table-thead>tr>th]:text-white/60 [&_.ant-table-tbody>tr>td]:bg-transparent [&_.ant-table-tbody>tr:hover>td]:bg-white/5"
          />
        </Card>
      </div>

      <Modal
        title={<span className="text-white">Yeni Paket</span>}
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={null}
        className="[&_.ant-modal-content]:bg-gray-800 [&_.ant-modal-header]:bg-transparent [&_.ant-modal-title]:text-white"
      >
        <Form
          form={form}
          layout="vertical"
          className="space-y-4"
        >
          <Form.Item
            name="name"
            label={<span className="text-white/80">Paket Adı</span>}
            rules={[{ required: true, message: 'Lütfen paket adı giriniz!' }]}
          >
            <Input className="bg-white/10 border-0 text-white" />
          </Form.Item>

          <Form.Item
            name="price"
            label={<span className="text-white/80">Fiyat (TON)</span>}
            rules={[{ required: true, message: 'Lütfen fiyat giriniz!' }]}
          >
            <InputNumber
              className="w-full bg-white/10 border-0 [&_.ant-input-number-input]:text-white"
              min={0}
              step={10}
            />
          </Form.Item>

          <Form.Item
            name="duration"
            label={<span className="text-white/80">Süre (gün)</span>}
            rules={[{ required: true, message: 'Lütfen süre giriniz!' }]}
          >
            <InputNumber
              className="w-full bg-white/10 border-0 [&_.ant-input-number-input]:text-white"
              min={1}
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 border-0"
            >
              Oluştur
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      <Navigation />
    </div>
  );
};

export default Packages; 