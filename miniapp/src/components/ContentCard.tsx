import React from 'react';
import { Link } from 'react-router-dom';

interface ContentCardProps {
  id: string;
  title: string;
  thumbnail: string;
  creatorName: string;
  creatorId: string;
  creatorAvatar: string;
  price?: number;
  isPremium: boolean;
  likes: number;
  category: string;
  previewText?: string;
  isSubscribed?: boolean;
  onClick?: (id: string) => void;
}

const ContentCard: React.FC<ContentCardProps> = ({
  id,
  title,
  thumbnail,
  creatorName,
  creatorId,
  creatorAvatar,
  price,
  isPremium,
  likes,
  category,
  previewText,
  isSubscribed = false,
  onClick
}) => {
  // Kategori ikonları
  const getCategoryIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case 'photo':
        return '📸';
      case 'video':
        return '🎬';
      case 'audio':
        return '🎧';
      case 'text':
        return '📝';
      default:
        return '📄';
    }
  };
  
  const handleClick = () => {
    if (onClick) {
      onClick(id);
    }
  };
  
  const canAccess = !isPremium || isSubscribed;
  
  return (
    <div 
      className={`
        bg-gradient-to-br 
        from-gray-900 to-black
        rounded-xl overflow-hidden 
        shadow-lg border border-gray-800
        transition duration-300 hover:shadow-pink-900/20 hover:border-pink-500/30
        cursor-pointer
        ${isPremium && !isSubscribed ? 'opacity-90' : ''}
      `}
      onClick={handleClick}
    >
      {/* Küçük resim alanı */}
      <div className="relative">
        <img 
          src={thumbnail} 
          alt={title}
          className={`w-full h-48 object-cover ${!canAccess ? 'filter blur-sm' : ''}`}
        />
        
        {/* Premium rozeti */}
        {isPremium && (
          <div className="absolute top-2 right-2 bg-gradient-to-r from-yellow-500 to-amber-500 text-white text-xs font-bold px-2 py-1 rounded-full">
            PREMIUM
          </div>
        )}
        
        {/* Kategori rozeti */}
        <div className="absolute top-2 left-2 bg-black/60 text-white text-xs px-2 py-1 rounded-full backdrop-blur-sm">
          {getCategoryIcon(category)} {category.charAt(0).toUpperCase() + category.slice(1)}
        </div>
        
        {/* Fiyat etiketi */}
        {isPremium && price && !isSubscribed && (
          <div className="absolute bottom-2 right-2 bg-black/60 text-white px-2 py-1 rounded-full backdrop-blur-sm text-sm font-bold">
            {price} Star
          </div>
        )}
        
        {/* Kilit ikonu */}
        {isPremium && !isSubscribed && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-4xl text-white/70">🔒</div>
          </div>
        )}
      </div>
      
      {/* İçerik bilgileri */}
      <div className="p-4">
        <h3 className="font-bold text-lg text-white mb-1 line-clamp-1">{title}</h3>
        
        {/* İçerik önizleme metni */}
        {previewText && (
          <p className="text-gray-400 text-sm mb-3 line-clamp-2">{previewText}</p>
        )}
        
        {/* Şovcu bilgileri */}
        <div className="flex items-center justify-between mt-2">
          <Link 
            to={`/creator/${creatorId}`}
            className="flex items-center space-x-2 group"
            onClick={(e) => e.stopPropagation()}
          >
            <img 
              src={creatorAvatar} 
              alt={creatorName}
              className="w-6 h-6 rounded-full border border-pink-500/50" 
            />
            <span className="text-gray-400 text-sm group-hover:text-pink-400 transition">{creatorName}</span>
          </Link>
          
          {/* Beğeni sayısı */}
          <div className="flex items-center space-x-1 text-gray-400">
            <span className="text-xs">❤️</span>
            <span className="text-xs">{likes}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContentCard; 