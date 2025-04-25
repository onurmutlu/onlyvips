import React, { useEffect, useState } from 'react';
import { Card, Button, Input, message, Modal, Form, InputNumber, Spin } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { usePackages } from '../hooks/usePackages';
import { formatCurrency } from '../utils/format';

const { TextArea } = Input;

interface PackageFormData {
  name: string;
  description: string;
  price: number;
  duration: number;
  features: string[];
}

const Packages: React.FC = () => {
  const { packages, loading, error, fetchPackages, createPackage, updatePackage, deletePackage } = usePackages();
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingPackage, setEditingPackage] = useState<string | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchPackages();
  }, []);

  const handleSubmit = async (values: PackageFormData) => {
    try {
      if (editingPackage) {
        await updatePackage(editingPackage, values);
        message.success('Paket güncellendi');
      } else {
        await createPackage(values);
        message.success('Paket oluşturuldu');
      }
      setIsModalVisible(false);
      form.resetFields();
      setEditingPackage(null);
    } catch (error) {
      message.error('Bir hata oluştu');
    }
  };

  const handleEdit = (pkg: any) => {
    setEditingPackage(pkg.id);
    form.setFieldsValue({
      ...pkg,
      features: pkg.features.join('\n'),
    });
    setIsModalVisible(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await deletePackage(id);
      message.success('Paket silindi');
    } catch (error) {
      message.error('Bir hata oluştu');
    }
  };

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
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold mb-2">VIP Paketlerim</h1>
          <p className="text-gray-500">VIP paketlerinizi yönetin ve yeni paketler oluşturun</p>
        </div>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setIsModalVisible(true)}
        >
          Yeni Paket
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {packages.map((pkg) => (
          <Card
            key={pkg.id}
            className="h-full"
            actions={[
              <Button
                key="edit"
                type="text"
                icon={<EditOutlined />}
                onClick={() => handleEdit(pkg)}
              />,
              <Button
                key="delete"
                type="text"
                danger
                icon={<DeleteOutlined />}
                onClick={() => handleDelete(pkg.id)}
              />,
            ]}
          >
            <Card.Meta
              title={
                <div className="flex justify-between items-center">
                  <span>{pkg.name}</span>
                  <span className="text-lg font-semibold">{formatCurrency(pkg.price)}</span>
                </div>
              }
              description={
                <div>
                  <p className="mb-4">{pkg.description}</p>
                  <div className="mb-4">
                    <span className="text-gray-500">Süre:</span>{' '}
                    <span className="font-medium">{pkg.duration} gün</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Özellikler:</span>
                    <ul className="list-disc list-inside mt-2">
                      {pkg.features.map((feature, index) => (
                        <li key={index} className="text-gray-700">{feature}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              }
            />
          </Card>
        ))}
      </div>

      <Modal
        title={editingPackage ? 'Paket Düzenle' : 'Yeni Paket'}
        open={isModalVisible}
        onCancel={() => {
          setIsModalVisible(false);
          form.resetFields();
          setEditingPackage(null);
        }}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="name"
            label="Paket Adı"
            rules={[{ required: true, message: 'Lütfen paket adı girin' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="description"
            label="Açıklama"
            rules={[{ required: true, message: 'Lütfen açıklama girin' }]}
          >
            <TextArea rows={4} />
          </Form.Item>

          <Form.Item
            name="price"
            label="Fiyat"
            rules={[{ required: true, message: 'Lütfen fiyat girin' }]}
          >
            <InputNumber
              min={0}
              step={0.01}
              className="w-full"
              formatter={(value) => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
              parser={(value) => value!.replace(/\$\s?|(,*)/g, '')}
            />
          </Form.Item>

          <Form.Item
            name="duration"
            label="Süre (Gün)"
            rules={[{ required: true, message: 'Lütfen süre girin' }]}
          >
            <InputNumber min={1} className="w-full" />
          </Form.Item>

          <Form.Item
            name="features"
            label="Özellikler"
            rules={[{ required: true, message: 'Lütfen en az bir özellik girin' }]}
          >
            <TextArea
              rows={4}
              placeholder="Her satıra bir özellik yazın"
            />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" className="w-full">
              {editingPackage ? 'Güncelle' : 'Oluştur'}
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Packages; 