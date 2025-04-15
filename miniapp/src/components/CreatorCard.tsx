import React from 'react';
import { Link } from 'react-router-dom';

interface CreatorCardProps {
  id: string;
  name: string;
  avatar: string;
  coverImage: string;
  bio: string;
  statistics: {
    contentCount: number;
    subscriberCount: number;
    likes: number;
  };
  tags: string[];
  featuredPackage?: {
    id: string;
    name: string;
    price: number;
  };
  isVerified: boolean;
  isOnline?: boolean;
}

const CreatorCard: React.FC<CreatorCardProps> = ({
  id,
  name,
  avatar,
  coverImage,
  bio,
  statistics,
  tags,
  featuredPackage,
  isVerified,
  isOnline
}) => {
  return (
    <Link to={`/creator/${id}`} className="block">
      <div className="bg-black/30 border border-white/10 rounded-xl overflow-hidden shadow-lg transition-all duration-300 hover:scale-[1.02] hover:shadow-pink-500/10">
        {/* Kapak fotoğrafı */}
        <div className="relative h-32">
          <img 
            src={coverImage} 
            alt={`${name} kapak fotoğrafı`} 
            className="w-full h-full object-cover"
          />
          
          {/* Avatar */}
          <div className="absolute -bottom-6 left-4">
            <div className="relative">
              <img 
                src={avatar} 
                alt={name} 
                className="w-16 h-16 rounded-full border-2 border-pink-500 object-cover"
              />
              
              {/* Online/Offline durumu */}
              {isOnline !== undefined && (
                <div 
                  className={`absolute bottom-0 right-0 w-4 h-4 rounded-full border-2 border-black ${
                    isOnline ? 'bg-emerald-500' : 'bg-gray-500'
                  }`}
                />
              )}
              
              {/* Doğrulanmış rozeti */}
              {isVerified && (
                <div className="absolute -top-1 -right-1 bg-blue-500 text-white p-1 rounded-full w-5 h-5 flex items-center justify-center text-xs">
                  ✓
                </div>
              )}
            </div>
          </div>
        </div>
        
        {/* İçerik */}
        <div className="pt-8 px-4 pb-4">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-white font-semibold text-lg">
                {name} {isVerified && '✓'}
              </h3>
              <p className="text-gray-300 text-sm mt-1 line-clamp-2">{bio}</p>
            </div>
          </div>
          
          {/* İstatistikler */}
          <div className="mt-3 flex justify-between text-xs text-gray-300">
            <div className="flex flex-col items-center">
              <span className="font-semibold text-white">{statistics.contentCount}</span>
              <span>İçerik</span>
            </div>
            <div className="flex flex-col items-center">
              <span className="font-semibold text-white">{statistics.subscriberCount}</span>
              <span>Abone</span>
            </div>
            <div className="flex flex-col items-center">
              <span className="font-semibold text-white">{statistics.likes}</span>
              <span>Beğeni</span>
            </div>
          </div>
          
          {/* Etiketler */}
          <div className="mt-3 flex flex-wrap gap-1">
            {tags.map((tag, index) => (
              <span 
                key={index} 
                className="text-xs bg-white/10 text-white/80 px-2 py-1 rounded-full"
              >
                {tag}
              </span>
            ))}
          </div>
          
          {/* Öne çıkan paket */}
          {featuredPackage && (
            <div className="mt-4 bg-gradient-to-r from-pink-500/20 to-purple-600/20 rounded-lg p-3">
              <div className="flex justify-between items-center">
                <div>
                  <span className="text-xs text-pink-300">Öne Çıkan Paket</span>
                  <p className="text-white font-medium">{featuredPackage.name}</p>
                </div>
                <button className="bg-gradient-to-r from-pink-500 to-purple-600 text-white text-sm px-3 py-1 rounded-lg">
                  {featuredPackage.price} Star
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </Link>
  );
};

export default CreatorCard; 