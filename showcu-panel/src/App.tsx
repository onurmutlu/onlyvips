import React, { useEffect } from 'react';
import { ConfigProvider, theme } from 'antd';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from 'antd';
import { telegramService } from './services/telegramService';
import Header from './components/layout/Header';
import Navigation from './components/layout/Navigation';
import Dashboard from './pages/Dashboard';
import MyContents from './pages/MyContents';
import ContentDetail from './pages/ContentDetail';
import Wallet from './pages/Wallet';
import Profile from './pages/Profile';
import { TonConnectUIProvider, THEME } from '@tonconnect/ui-react';
import WebApp from '@twa-dev/sdk';

const { Content } = Layout;

const manifestUrl = 'https://raw.githubusercontent.com/onlyvips/tonconnect-manifest/main/manifest.json';

const App: React.FC = () => {
  useEffect(() => {
    telegramService.init();
    WebApp.ready();
    WebApp.setHeaderColor('#0088cc');
    WebApp.setBackgroundColor('#1a1a1a');
  }, []);

  return (
    <TonConnectUIProvider 
      manifestUrl={manifestUrl} 
      key="ton-connect"
      uiPreferences={{ theme: THEME.DARK }}
    >
      <ConfigProvider
        theme={{
          algorithm: theme.darkAlgorithm,
          token: {
            colorPrimary: '#0088cc',
            borderRadius: 8,
            fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
          },
          components: {
            Layout: {
              headerBg: 'transparent',
              bodyBg: 'transparent',
            },
            Card: {
              borderRadius: 12,
            },
            Button: {
              borderRadius: 8,
            },
            Input: {
              borderRadius: 8,
            },
            Select: {
              borderRadius: 8,
            },
          },
        }}
      >
        <Layout className="min-h-screen bg-gray-900">
          <Header />
          <Content className="p-6 pb-20">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/content" element={<MyContents />} />
              <Route path="/contents" element={<MyContents />} />
              <Route path="/contents/:id" element={<ContentDetail />} />
              <Route path="/wallet" element={<Wallet />} />
              <Route path="/profile" element={<Profile />} />
            </Routes>
          </Content>
          <Navigation />
        </Layout>
      </ConfigProvider>
    </TonConnectUIProvider>
  );
};

export default App; 