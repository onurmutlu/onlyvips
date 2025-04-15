import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTelegramContext } from '../TelegramProvider';
import { useAuth } from '../hooks/useAuth';

const Login = () => {
  const navigate = useNavigate();
  const { tg, user, isReady } = useTelegramContext();
  const { isAuthenticated, isShowcu, loading, error } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      if (isShowcu) {
        // Showcu rolüne sahipse ana sayfaya yönlendir
        navigate('/');
      } else {
        // Showcu değilse hata göster
        alert('Bu panel sadece şovcular içindir. Lütfen şovcu hesabınızla giriş yapın.');
        if (tg) {
          tg.close(); // Telegram MiniApp'i kapat
        }
      }
    }
  }, [isAuthenticated, isShowcu, navigate, tg]);

  return (
    <div className="min-h-screen bg-gradient-dark flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold gradient-text mb-2">Şovcu Paneli</h1>
          <p className="text-text-muted">Erotik içeriklerinizi yönetin ve kazanç sağlayın</p>
        </div>

        <div className="bg-bg-card rounded-lg shadow-lg p-6 border border-border-color">
          {loading ? (
            <div className="flex justify-center items-center py-10">
              <div className="loading-spinner"></div>
            </div>
          ) : error ? (
            <div className="text-center py-6">
              <div className="i-mdi-alert-circle text-4xl text-error mx-auto mb-3"></div>
              <h2 className="text-xl font-medium mb-2">Giriş Hatası</h2>
              <p className="text-text-muted mb-4">{error}</p>
              <button 
                onClick={() => window.location.reload()}
                className="btn-primary"
              >
                Tekrar Dene
              </button>
            </div>
          ) : isReady && user ? (
            <div className="text-center py-4">
              <div className="i-mdi-account-check text-4xl text-primary mx-auto mb-3"></div>
              <h2 className="text-xl font-medium mb-1">Hoş Geldiniz</h2>
              <p className="text-text-muted mb-6">Giriş yapılıyor, lütfen bekleyin...</p>
              <div className="loading-spinner mx-auto"></div>
            </div>
          ) : (
            <div className="text-center py-6">
              <div className="i-mdi-telegram text-5xl text-primary mx-auto mb-4"></div>
              <h2 className="text-xl font-medium mb-2">Telegram ile Giriş Yapın</h2>
              <p className="text-text-muted mb-6">
                Telegram MiniApp otomatik olarak sizi tanıyacaktır. Eğer giriş yapamıyorsanız 
                lütfen sayfayı yenileyin veya uygulamayı kapatıp tekrar açın.
              </p>
              
              <p className="text-sm text-text-muted mt-6">
                Not: Bu panel sadece onaylı şovcular tarafından kullanılabilir. 
                Şovcu olmak için bot ile iletişime geçin.
              </p>
            </div>
          )}
        </div>
        
        <div className="text-center mt-8">
          <p className="text-text-muted text-sm">
            &copy; {new Date().getFullYear()} OnlyVips by SiyahKare
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login; 