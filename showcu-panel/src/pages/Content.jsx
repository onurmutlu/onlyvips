import { useState, useEffect } from 'react';
import { getContents, deleteContent } from '../api/content';
import ContentForm from '../components/content/ContentForm';
import ContentList from '../components/content/ContentList';
import { useTelegramContext } from '../TelegramProvider';

export default function Content() {
  const { tg } = useTelegramContext();
  const [contents, setContents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  
  const fetchContents = async () => {
    setLoading(true);
    try {
      const data = await getContents();
      setContents(data);
      setError(null);
    } catch (err) {
      setError('İçerikler yüklenirken bir hata oluştu');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchContents();
    
    // Telegram ana butonu yapılandır
    if (tg?.MainButton) {
      tg.MainButton.setText('Yeni İçerik Ekle');
      tg.MainButton.show();
      
      const handleMainButton = () => {
        setShowForm(prev => !prev);
        tg.MainButton.setText(showForm ? 'Yeni İçerik Ekle' : 'İptal');
      };
      
      tg.onEvent('mainButtonClicked', handleMainButton);
      
      return () => {
        tg.offEvent('mainButtonClicked', handleMainButton);
        tg.MainButton.hide();
      };
    }
  }, [tg, showForm]);
  
  const handleContentSubmit = async (contentData, file) => {
    try {
      // API'ye veri gönder
      // ...
      
      fetchContents(); // İçerikleri yeniden yükle
      setShowForm(false);
      tg?.MainButton?.setText('Yeni İçerik Ekle');
    } catch (err) {
      console.error('İçerik yüklenirken hata:', err);
      alert('İçerik yüklenemedi');
    }
  };
  
  // ... geri kalanı
}
