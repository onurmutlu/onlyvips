import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { TelegramProvider } from './TelegramProvider';
import { useAuth } from './hooks/useAuth';

// Layouts
import AppLayout from './components/layout/AppLayout';

// Pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Content from './pages/Content';
import Packages from './pages/Packages';
import Stats from './pages/Stats';
import Profile from './pages/Profile';

function ProtectedRoute({ children }) {
  const { isAuthenticated, isShowcu, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-bg-main">
        <div className="loading-spinner"></div>
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  if (!isShowcu) {
    return (
      <div className="h-screen w-screen flex flex-col items-center justify-center bg-bg-main p-4 text-center">
        <div className="i-mdi-account-off text-5xl text-error mb-4"></div>
        <h1 className="text-2xl font-bold mb-2">Yetkisiz Erişim</h1>
        <p className="text-text-muted mb-6">
          Bu panel yalnızca onaylı şovcular tarafından kullanılabilir.
        </p>
        <button 
          onClick={() => window.Telegram?.WebApp?.close()} 
          className="btn-primary"
        >
          Geri Dön
        </button>
      </div>
    );
  }
  
  return children;
}

function AuthProvider({ children }) {
  return (
    <TelegramProvider>
      {children}
    </TelegramProvider>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          
          <Route path="/" element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }>
            <Route index element={<Dashboard />} />
            <Route path="content" element={<Content />} />
            <Route path="packages" element={<Packages />} />
            <Route path="stats" element={<Stats />} />
            <Route path="profile" element={<Profile />} />
          </Route>
          
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App; 