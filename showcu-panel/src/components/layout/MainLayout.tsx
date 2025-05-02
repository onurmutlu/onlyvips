import React from 'react';
import { Layout } from 'antd';
import Header from './Header';
import Sidebar from './Sidebar';
import { useTelegram } from '../../hooks/useTelegram';

const { Content } = Layout;

const MainLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isMiniApp } = useTelegram();

  return (
    <Layout className="min-h-screen bg-transparent">
      {!isMiniApp && <Header />}
      <Layout className="flex flex-row">
        {!isMiniApp && <Sidebar />}
        <Content className="p-4 md:p-6 overflow-auto">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout; 