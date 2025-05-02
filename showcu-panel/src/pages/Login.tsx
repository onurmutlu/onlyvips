import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Input, Button, Card, message } from 'antd';
import { useAuth } from '../hooks/useAuth';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const { login, isAuthenticated } = useAuth();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    try {
      const success = await login(values.username, values.password);
      if (success) {
        message.success('Giriş başarılı!');
        navigate('/dashboard');
      } else {
        message.error('Geçersiz kullanıcı adı veya şifre!');
      }
    } catch (error) {
      message.error('Bir hata oluştu!');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900">
      <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))]"></div>
      <Card 
        className="w-[400px] bg-white/10 backdrop-blur-lg border-0 shadow-lg"
        title={
          <div className="text-center text-white text-2xl font-bold">
            OnlyVips Giriş
          </div>
        }
      >
        <Form
          name="login"
          initialValues={{ remember: true }}
          onFinish={onFinish}
          layout="vertical"
          className="space-y-4"
        >
          <Form.Item
            label={<span className="text-white">Kullanıcı Adı</span>}
            name="username"
            rules={[{ required: true, message: 'Lütfen kullanıcı adınızı girin!' }]}
          >
            <Input 
              className="bg-white/20 border-0 text-white placeholder:text-white/50"
              placeholder="demo" 
            />
          </Form.Item>

          <Form.Item
            label={<span className="text-white">Şifre</span>}
            name="password"
            rules={[{ required: true, message: 'Lütfen şifrenizi girin!' }]}
          >
            <Input.Password 
              className="bg-white/20 border-0 text-white placeholder:text-white/50"
              placeholder="demo123" 
            />
          </Form.Item>

          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit" 
              loading={loading} 
              block
              className="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 border-0 h-10 text-lg font-semibold"
            >
              Giriş Yap
            </Button>
          </Form.Item>

          <div className="text-center text-white/80 space-y-2">
            <p className="font-medium">Demo Giriş Bilgileri:</p>
            <p><strong>Kullanıcı Adı:</strong> demo</p>
            <p><strong>Şifre:</strong> demo123</p>
          </div>
        </Form>
      </Card>
    </div>
  );
};

export default Login; 