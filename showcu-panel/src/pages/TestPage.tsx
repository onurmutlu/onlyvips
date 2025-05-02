import React from 'react';
import { telegramService } from '../services/telegramService';

const TestPage: React.FC = () => {
  const user = telegramService.getUser();
  const isMiniApp = telegramService.isMiniApp();
  const theme = telegramService.getTheme();
  const platform = telegramService.getPlatform();

  const handleAlert = () => {
    telegramService.showAlert('Bu bir test mesajıdır!');
  };

  const handleConfirm = () => {
    telegramService.showConfirm('Onaylıyor musunuz?', (result) => {
      console.log('Onay sonucu:', result);
    });
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Test Sayfası</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <h2>Kullanıcı Bilgileri</h2>
        <pre>{JSON.stringify(user, null, 2)}</pre>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h2>Sistem Bilgileri</h2>
        <p>MiniApp: {isMiniApp ? 'Evet' : 'Hayır'}</p>
        <p>Tema: {theme}</p>
        <p>Platform: {platform}</p>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h2>Test Butonları</h2>
        <button onClick={handleAlert} style={{ marginRight: '10px' }}>
          Alert Göster
        </button>
        <button onClick={handleConfirm}>
          Onay İste
        </button>
      </div>
    </div>
  );
};

export default TestPage; 