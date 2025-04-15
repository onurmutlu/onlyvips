import React from 'react';
import { Link } from 'react-router-dom';

const TopContents = ({ contents = [] }) => {
  if (!contents || contents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-10">
        <div className="i-mdi-movie-off text-5xl text-text-muted mb-3"></div>
        <p className="text-text-muted">Henüz içerik yüklenmemiş</p>
        <Link to="/content" className="mt-4 btn-primary">
          İçerik Ekle
        </Link>
      </div>
    );
  }

  // Görüntüleme türü ikonları
  const getTypeIcon = (type) => {
    switch (type) {
      case 'photo':
        return 'i-mdi-image text-info';
      case 'video':
        return 'i-mdi-video text-error';
      case 'audio':
        return 'i-mdi-music-note text-success';
      default:
        return 'i-mdi-file-document text-text-muted';
    }
  };

  // Erişim türü ayarları
  const getAccessBadge = (accessType) => {
    switch (accessType) {
      case 'free':
        return (
          <span className="text-xs bg-info bg-opacity-10 text-info px-2 py-0.5 rounded-full">
            Ücretsiz
          </span>
        );
      case 'vip':
        return (
          <span className="text-xs bg-primary bg-opacity-10 text-primary px-2 py-0.5 rounded-full">
            VIP
          </span>
        );
      case 'premium':
        return (
          <span className="text-xs bg-warning bg-opacity-10 text-warning px-2 py-0.5 rounded-full">
            Premium
          </span>
        );
      case 'nft':
        return (
          <span className="text-xs bg-success bg-opacity-10 text-success px-2 py-0.5 rounded-full">
            NFT
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <ul className="divide-y divide-border-color">
      {contents.map((content) => (
        <li key={content.id} className="py-3">
          <Link to={`/content/${content.id}`} className="flex items-center gap-3">
            <div className="relative flex-shrink-0">
              <div className="w-14 h-14 rounded-md overflow-hidden">
                <img
                  src={content.thumbnail_url}
                  alt={content.title}
                  className="w-full h-full object-cover"
                />
              </div>
              <div className={`${getTypeIcon(content.type)} absolute top-1 right-1 p-1 rounded-full bg-bg-card bg-opacity-80`}></div>
            </div>
            
            <div className="flex-grow min-w-0">
              <div className="flex justify-between">
                <h3 className="font-medium text-white truncate">{content.title}</h3>
              </div>
              
              <div className="flex items-center text-xs text-text-muted mt-1">
                <div className="i-mdi-eye mr-1"></div>
                <span>{content.views}</span>
                <div className="i-mdi-cash mx-1 ml-3"></div>
                <span>{content.revenue} TON</span>
              </div>
              
              <div className="flex items-center gap-2 mt-1">
                {getAccessBadge(content.access_type)}
                {content.is_featured && (
                  <span className="text-xs bg-warning bg-opacity-10 text-warning px-2 py-0.5 rounded-full">
                    Öne Çıkan
                  </span>
                )}
              </div>
            </div>
            
            <div className="i-mdi-chevron-right text-text-muted"></div>
          </Link>
        </li>
      ))}
    </ul>
  );
};

export default TopContents; 