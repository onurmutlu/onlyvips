import React, { useState } from 'react';
import { Card, Form, Input, Button, Upload, message, Avatar, Tabs, Tag } from 'antd';
import { UserOutlined, CameraOutlined, SaveOutlined, LockOutlined, BellOutlined, SecurityScanOutlined } from '@ant-design/icons';

const Profile: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('1');

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      message.success('Profil başarıyla güncellendi!');
    } catch (error) {
      message.error('Bir hata oluştu!');
    } finally {
      setLoading(false);
    }
  };

  const items = [
    {
      key: '1',
      label: 'Profil Bilgileri',
      children: (
        <Form
          form={form}
          layout="vertical"
          onFinish={onFinish}
          className="space-y-4"
        >
          <div className="text-center mb-8">
            <div className="relative inline-block">
              <Avatar 
                size={120} 
                icon={<UserOutlined />}
                className="bg-purple-500/20 border-2 border-white/20"
              />
              <Upload 
                showUploadList={false}
                className="absolute bottom-0 right-0"
              >
                <Button 
                  shape="circle" 
                  icon={<CameraOutlined />}
                  className="bg-purple-500 border-0 hover:bg-purple-600"
                />
              </Upload>
            </div>
          </div>

          <Form.Item
            name="name"
            label={<span className="text-white/80">Ad Soyad</span>}
            rules={[{ required: true, message: 'Lütfen ad soyad giriniz!' }]}
          >
            <Input 
              className="bg-white/10 border-0 text-white placeholder:text-white/50"
              placeholder="Ad Soyad"
            />
          </Form.Item>

          <Form.Item
            name="email"
            label={<span className="text-white/80">E-posta</span>}
            rules={[
              { required: true, message: 'Lütfen e-posta giriniz!' },
              { type: 'email', message: 'Geçerli bir e-posta adresi giriniz!' }
            ]}
          >
            <Input 
              className="bg-white/10 border-0 text-white placeholder:text-white/50"
              placeholder="E-posta"
            />
          </Form.Item>

          <Form.Item
            name="bio"
            label={<span className="text-white/80">Hakkımda</span>}
          >
            <Input.TextArea
              rows={4}
              className="bg-white/10 border-0 text-white placeholder:text-white/50"
              placeholder="Kendiniz hakkında kısa bir bilgi yazın..."
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              icon={<SaveOutlined />}
              className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 border-0 h-10 text-lg font-semibold"
            >
              Kaydet
            </Button>
          </Form.Item>
        </Form>
      ),
    },
    {
      key: '2',
      label: 'Güvenlik',
      children: (
        <div className="space-y-6">
          <Card className="bg-white/5 backdrop-blur-lg border-0">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold flex items-center">
                  <LockOutlined className="mr-2" />
                  Şifre Değiştir
                </h3>
                <p className="text-white/60">Son değişiklik: 2 ay önce</p>
              </div>
              <Button type="primary" ghost>
                Değiştir
              </Button>
            </div>
          </Card>

          <Card className="bg-white/5 backdrop-blur-lg border-0">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold flex items-center">
                  <SecurityScanOutlined className="mr-2" />
                  İki Faktörlü Doğrulama
                </h3>
                <p className="text-white/60">Hesabınızı daha güvenli hale getirin</p>
              </div>
              <Button type="primary" ghost>
                Etkinleştir
              </Button>
            </div>
          </Card>
        </div>
      ),
    },
    {
      key: '3',
      label: 'Bildirimler',
      children: (
        <div className="space-y-6">
          <Card className="bg-white/5 backdrop-blur-lg border-0">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold flex items-center">
                  <BellOutlined className="mr-2" />
                  E-posta Bildirimleri
                </h3>
                <p className="text-white/60">Yeni içerik ve ödeme bildirimleri</p>
              </div>
              <Tag color="green">Aktif</Tag>
            </div>
          </Card>

          <Card className="bg-white/5 backdrop-blur-lg border-0">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold flex items-center">
                  <BellOutlined className="mr-2" />
                  Telegram Bildirimleri
                </h3>
                <p className="text-white/60">Anlık bildirimler için Telegram botu</p>
              </div>
              <Tag color="green">Aktif</Tag>
            </div>
          </Card>
        </div>
      ),
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-indigo-900 text-white">
      <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))]"></div>
      
      <div className="container mx-auto px-4 py-8 relative z-10">
        <h1 className="text-3xl font-bold mb-8">Profil Ayarları</h1>

        <Card className="bg-white/5 backdrop-blur-lg border-0 shadow-xl">
          <Tabs
            activeKey={activeTab}
            onChange={setActiveTab}
            items={items}
            className="[&_.ant-tabs-tab]:text-white/60 [&_.ant-tabs-tab-active]:text-white [&_.ant-tabs-ink-bar]:bg-purple-500"
          />
        </Card>
      </div>
    </div>
  );
};

export default Profile; 