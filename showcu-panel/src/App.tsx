import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from 'antd';
import { useAuth } from './hooks/useAuth';
import { telegramService } from './services';

// Pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Content from './pages/Content';
import Packages from './pages/Packages';
import Subscribers from './pages/Subscribers';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';

// Components
import AppHeader from './components/layout/Header';
import Navigation from './components/layout/Navigation';

const { Content: AntContent } = Layout;

const App: React.FC = () => {
  const { isAuthenticated } = useAuth();

  React.useEffect(() => {
    telegramService.init();
  }, []);

  if (!isAuthenticated) {
    return <Login />;
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <AppHeader />
      <Layout>
        <Navigation />
        <Layout style={{ padding: '24px' }}>
          <AntContent>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/content" element={<Content />} />
              <Route path="/packages" element={<Packages />} />
              <Route path="/subscribers" element={<Subscribers />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </AntContent>
        </Layout>
      </Layout>
    </Layout>
  );
};

export default App; 