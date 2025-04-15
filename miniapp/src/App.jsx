import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { TelegramProvider } from './TelegramProvider';

// Layouts
import AppLayout from './components/layout/AppLayout';

// Pages
import Home from './pages/Home';
import ContentDetail from './pages/ContentDetail';
import ShowcuProfile from './pages/ShowcuProfile';
import VipPackages from './pages/VipPackages';
import UserProfile from './pages/UserProfile';

function App() {
  return (
    <TelegramProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<AppLayout />}>
            <Route index element={<Home />} />
            <Route path="content/:id" element={<ContentDetail />} />
            <Route path="showcu/:id" element={<ShowcuProfile />} />
            <Route path="packages" element={<VipPackages />} />
            <Route path="profile" element={<UserProfile />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </TelegramProvider>
  );
}

export default App;
