import React, { useState } from 'react';
import { Card, Form, Input, Button, Switch, message, Spin, Upload } from 'antd';
import { UserOutlined, MailOutlined, LockOutlined, UploadOutlined } from '@ant-design/icons';
import { useAuth } from '../hooks/useAuth';
import { storageService } from '../services';

const Settings: React.FC = () => {
  const { user, updateProfile } = useAuth();
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();

  const handleSubmit = async (values: any) => {
    try {
      setLoading(true);
      await updateProfile(values);
      message.success('Profil güncellendi');
    } catch (error) {
      message.error('Bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (file: File) => {
    try {
      const response = await storageService.uploadImage(file);
      form.setFieldValue('avatar', response.url);
      message.success('Profil fotoğrafı güncellendi');
    } catch (error) {
      message.error('Dosya yüklenirken bir hata oluştu');
    }
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">Ayarlar</h1>
        <p className="text-gray-500">Hesap ayarlarınızı yönetin</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Profil Bilgileri">
          <Form
            form={form}
            layout="vertical"
            initialValues={user}
            onFinish={handleSubmit}
          >
            <Form.Item
              name="avatar"
              label="Profil Fotoğrafı"
            >
              <Upload
                customRequest={async ({ file }) => {
                  await handleUpload(file as File);
                }}
                showUploadList={false}
              >
                <Button icon={<UploadOutlined />}>Fotoğraf Yükle</Button>
              </Upload>
            </Form.Item>

            <Form.Item
              name="username"
              label="Kullanıcı Adı"
              rules={[{ required: true, message: 'Lütfen kullanıcı adı girin' }]}
            >
              <Input prefix={<UserOutlined />} />
            </Form.Item>

            <Form.Item
              name="email"
              label="E-posta"
              rules={[
                { required: true, message: 'Lütfen e-posta girin' },
                { type: 'email', message: 'Geçerli bir e-posta adresi girin' },
              ]}
            >
              <Input prefix={<MailOutlined />} />
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading} className="w-full">
                Kaydet
              </Button>
            </Form.Item>
          </Form>
        </Card>

        <Card title="Güvenlik">
          <Form layout="vertical">
            <Form.Item
              name="currentPassword"
              label="Mevcut Şifre"
            >
              <Input.Password prefix={<LockOutlined />} />
            </Form.Item>

            <Form.Item
              name="newPassword"
              label="Yeni Şifre"
            >
              <Input.Password prefix={<LockOutlined />} />
            </Form.Item>

            <Form.Item
              name="confirmPassword"
              label="Yeni Şifre (Tekrar)"
            >
              <Input.Password prefix={<LockOutlined />} />
            </Form.Item>

            <Form.Item>
              <Button type="primary" className="w-full">
                Şifreyi Güncelle
              </Button>
            </Form.Item>
          </Form>
        </Card>

        <Card title="Bildirimler">
          <Form layout="vertical" initialValues={{ notifications: true }}>
            <Form.Item
              name="notifications"
              label="E-posta Bildirimleri"
              valuePropName="checked"
            >
              <Switch />
            </Form.Item>

            <Form.Item>
              <Button type="primary" className="w-full">
                Bildirim Ayarlarını Kaydet
              </Button>
            </Form.Item>
          </Form>
        </Card>

        <Card title="Hesap">
          <div className="space-y-4">
            <div>
              <h3 className="font-medium mb-2">Hesap Silme</h3>
              <p className="text-gray-500 mb-4">
                Hesabınızı silmek istediğinizden emin misiniz? Bu işlem geri alınamaz.
              </p>
              <Button danger>
                Hesabı Sil
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Settings; 