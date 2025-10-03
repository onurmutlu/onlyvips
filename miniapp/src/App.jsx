import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { TelegramProvider } from './TelegramProvider';

// Layouts
import AppLayout from './components/layout/AppLayout';

// Pages
import Home from './pages/Home';
import ContentDetail from './pages/ContentDetail';
import ShowcuProfile from './pages/ShowcuProfile';
import VipPackages from './pages/VipPackages';
import UserProfile from './pages/UserProfile';
import CreatorProfile from './pages/CreatorProfile';
import TaskDetail from './pages/TaskDetail';

const App = () => {
  // Telegram WebApp kurulumu
  React.useEffect(() => {
    if (typeof window !== "undefined" && window.Telegram && window.Telegram?.WebApp) {
      const tg = window.Telegram.WebApp;
      tg.ready();
      tg.expand();
    }
  }, []);
  
  return (
    <TelegramProvider>
      <Router>
        <Routes>
          <Route path="/" element={<AppLayout />}>
            <Route index element={<Home />} />
            <Route path="content/:id" element={<ContentDetail />} />
            <Route path="showcu/:id" element={<ShowcuProfile />} />
            <Route path="packages" element={<VipPackages />} />
            <Route path="profile" element={<UserProfile />} />
            <Route path="creator/:creatorId" element={<CreatorProfile />} />
            <Route path="creator/:creatorId/task/:taskId" element={<TaskDetail />} />
          </Route>
        </Routes>
      </Router>
    </TelegramProvider>
  );
};

export default App;
