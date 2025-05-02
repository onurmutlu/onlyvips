import React from 'react';
import { Layout, Dropdown, Avatar, Space } from 'antd';
import { UserOutlined, SettingOutlined, LogoutOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useTelegram } from '../../hooks/useTelegram';

const { Header: AntHeader } = Layout;

const Header: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useTelegram();

  const menuItems = [
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Ayarlar',
      onClick: () => navigate('/settings'),
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Çıkış Yap',
      onClick: () => {
        // Çıkış işlemleri
        navigate('/login');
      },
    },
  ];

  return (
    <AntHeader className="bg-transparent border-b border-gray-800 flex items-center justify-between px-4">
      <div className="flex items-center">
        <h1 className="text-xl font-bold text-white">OnlyVips</h1>
      </div>
      <div className="flex items-center">
        <Dropdown
          menu={{ items: menuItems }}
          placement="bottomRight"
          trigger={['click']}
        >
          <Space className="cursor-pointer">
            <Avatar
              icon={<UserOutlined />}
              src={user?.photo_url}
              className="bg-primary"
            />
            <span className="text-white">
              {user?.first_name} {user?.last_name}
            </span>
          </Space>
        </Dropdown>
      </div>
    </AntHeader>
  );
};

export default Header; 