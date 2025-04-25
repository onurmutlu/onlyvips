import React, { useState } from 'react';
import { Form, Input, Button, Card, message, Spin } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useAuth } from '../hooks/useAuth';
import { telegramService } from '../services';

const Login: React.FC = () => {
  const { login } = useAuth();
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();

  const handleSubmit = async (values: { email: string; password: string }) => {
    try {
      setLoading(true);
      await login(values.email, values.password);
      message.success('Giriş başarılı');
    } catch (error) {
      message.error('Giriş başarısız');
    } finally {
      setLoading(false);
    }
  };

  const handleTelegramLogin = () => {
    const user = telegramService.getUser();
    if (user) {
      form.setFieldsValue({
        email: `${user.id}@telegram.user`,
        password: user.hash,
      });
      handleSubmit({
        email: `${user.id}@telegram.user`,
        password: user.hash,
      });
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <Card className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold mb-2">OnlyVips</h1>
          <p className="text-gray-500">Şovcu Paneline Hoş Geldiniz</p>
        </div>

        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="email"
            rules={[
              { required: true, message: 'Lütfen e-posta girin' },
              { type: 'email', message: 'Geçerli bir e-posta adresi girin' },
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="E-posta"
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: 'Lütfen şifre girin' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Şifre"
              size="large"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              size="large"
              className="w-full"
              loading={loading}
            >
              Giriş Yap
            </Button>
          </Form.Item>

          <div className="text-center">
            <Button
              type="link"
              onClick={handleTelegramLogin}
              className="text-blue-500"
            >
              Telegram ile Giriş Yap
            </Button>
          </div>
        </Form>
      </Card>
    </div>
  );
};

export default Login; 