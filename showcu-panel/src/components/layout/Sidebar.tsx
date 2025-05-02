import React from 'react';
import { Layout, Menu } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  FileImageOutlined,
  ShoppingCartOutlined,
  BarChartOutlined,
  SettingOutlined,
} from '@ant-design/icons';

const { Sider } = Layout;

const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: '/content',
      icon: <FileImageOutlined />,
      label: 'İçerikler',
    },
    {
      key: '/packages',
      icon: <ShoppingCartOutlined />,
      label: 'Paketler',
    },
    {
      key: '/analytics',
      icon: <BarChartOutlined />,
      label: 'Analitik',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: 'Ayarlar',
    },
  ];

  return (
    <Sider
      width={240}
      className="bg-transparent border-r border-gray-800"
      breakpoint="lg"
      collapsedWidth={0}
    >
      <div className="h-16 flex items-center justify-center">
        <h1 className="text-xl font-bold text-white">OnlyVips</h1>
      </div>
      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={[location.pathname]}
        items={menuItems}
        onClick={({ key }) => navigate(key)}
        className="bg-transparent"
      />
    </Sider>
  );
};

export default Sidebar; 