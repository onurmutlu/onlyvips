import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import api from '../api/creatorApi';

interface ContentUploaderProps {
  onSuccess: () => void;
}

type ContentFormData = {
  title: string;
  description: string;
  category: string;
  isPremium: boolean;
  price?: number;
  mediaType: 'photo' | 'video' | 'audio' | 'text';
  textContent?: string;
};

const ContentUploader: React.FC<ContentUploaderProps> = ({ onSuccess }) => {
  const [thumbnail, setThumbnail] = useState<File | null>(null);
  const [mediaFile, setMediaFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [thumbnailPreview, setThumbnailPreview] = useState<string | null>(null);
  
  const { register, handleSubmit, watch, formState: { errors } } = useForm<ContentFormData>();
  
  const selectedMediaType = watch('mediaType');
  const isPremium = watch('isPremium');
  
  const handleThumbnailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setThumbnail(file);
      
      // Önizleme oluştur
      const reader = new FileReader();
      reader.onloadend = () => {
        setThumbnailPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };
  
  const handleMediaFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setMediaFile(e.target.files[0]);
    }
  };
  
  const onSubmit = async (data: ContentFormData) => {
    try {
      setUploading(true);
      
      const formData = new FormData();
      
      // Form verilerini ekle
      Object.keys(data).forEach(key => {
        formData.append(key, data[key as keyof ContentFormData] as string);
      });
      
      // Dosyaları ekle
      if (thumbnail) {
        formData.append('thumbnail', thumbnail);
      }
      
      if (mediaFile && selectedMediaType !== 'text') {
        formData.append('mediaFile', mediaFile);
      }
      
      // API isteğini gönder
      const response = await api.createContent(formData);
      
      if (response.success) {
        alert('İçerik başarıyla yüklendi!');
        onSuccess(); // Başarılı işlem geri çağrısı
      } else {
        alert(`Hata: ${response.error}`);
      }
    } catch (error) {
      console.error('İçerik yükleme hatası:', error);
      alert('İçerik yüklenirken bir hata oluştu');
    } finally {
      setUploading(false);
    }
  };
  
  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h2 className="text-2xl font-bold text-white mb-6">Yeni İçerik Ekle</h2>
      
      <form onSubmit={handleSubmit(onSubmit)}>
        {/* Başlık */}
        <div className="mb-4">
          <label className="block text-white mb-2">Başlık</label>
          <input
            type="text"
            className="w-full p-2 bg-gray-700 text-white rounded-lg"
            {...register('title', { required: true })}
          />
          {errors.title && <span className="text-red-500">Başlık gerekli</span>}
        </div>
        
        {/* Açıklama */}
        <div className="mb-4">
          <label className="block text-white mb-2">Açıklama</label>
          <textarea
            className="w-full p-2 bg-gray-700 text-white rounded-lg"
            rows={4}
            {...register('description', { required: true })}
          />
          {errors.description && <span className="text-red-500">Açıklama gerekli</span>}
        </div>
        
        {/* Kategori */}
        <div className="mb-4">
          <label className="block text-white mb-2">Kategori</label>
          <select
            className="w-full p-2 bg-gray-700 text-white rounded-lg"
            {...register('category', { required: true })}
          >
            <option value="">Kategori Seçin</option>
            <option value="flirt">Flört</option>
            <option value="dating">Buluşma</option>
            <option value="relationship">İlişki</option>
            <option value="psychology">Psikoloji</option>
            <option value="lifestyle">Yaşam Tarzı</option>
          </select>
          {errors.category && <span className="text-red-500">Kategori gerekli</span>}
        </div>
        
        {/* Premium İçerik */}
        <div className="mb-4">
          <label className="flex items-center text-white">
            <input 
              type="checkbox" 
              className="mr-2" 
              {...register('isPremium')} 
            />
            Premium İçerik
          </label>
        </div>
        
        {/* Fiyat (Premium ise) */}
        {isPremium && (
          <div className="mb-4">
            <label className="block text-white mb-2">Fiyat (Star)</label>
            <input
              type="number"
              className="w-full p-2 bg-gray-700 text-white rounded-lg"
              {...register('price', { required: isPremium, min: 1 })}
            />
            {errors.price && <span className="text-red-500">Geçerli bir fiyat girin</span>}
          </div>
        )}
        
        {/* İçerik Tipi */}
        <div className="mb-4">
          <label className="block text-white mb-2">İçerik Tipi</label>
          <select
            className="w-full p-2 bg-gray-700 text-white rounded-lg"
            {...register('mediaType', { required: true })}
          >
            <option value="photo">Fotoğraf</option>
            <option value="video">Video</option>
            <option value="audio">Ses</option>
            <option value="text">Yazı</option>
          </select>
          {errors.mediaType && <span className="text-red-500">İçerik tipi gerekli</span>}
        </div>
        
        {/* Thumbnail */}
        <div className="mb-4">
          <label className="block text-white mb-2">Kapak Resmi</label>
          <input
            type="file"
            accept="image/*"
            className="w-full p-2 bg-gray-700 text-white rounded-lg"
            onChange={handleThumbnailChange}
          />
          
          {thumbnailPreview && (
            <div className="mt-2">
              <img src={thumbnailPreview} alt="Önizleme" className="h-40 object-cover rounded-lg" />
            </div>
          )}
        </div>
        
        {/* Medya Dosyası (Yazı hariç) */}
        {selectedMediaType !== 'text' && (
          <div className="mb-4">
            <label className="block text-white mb-2">
              {selectedMediaType === 'photo' ? 'Fotoğraf' : 
                selectedMediaType === 'video' ? 'Video' : 'Ses Dosyası'}
            </label>
            <input
              type="file"
              accept={
                selectedMediaType === 'photo' ? 'image/*' : 
                selectedMediaType === 'video' ? 'video/*' : 'audio/*'
              }
              className="w-full p-2 bg-gray-700 text-white rounded-lg"
              onChange={handleMediaFileChange}
            />
          </div>
        )}
        
        {/* Metin İçeriği (Yazı ise) */}
        {selectedMediaType === 'text' && (
          <div className="mb-4">
            <label className="block text-white mb-2">İçerik Metni</label>
            <textarea
              className="w-full p-2 bg-gray-700 text-white rounded-lg"
              rows={10}
              {...register('textContent', { required: selectedMediaType === 'text' })}
            />
            {errors.textContent && <span className="text-red-500">İçerik metni gerekli</span>}
          </div>
        )}
        
        {/* Gönder Butonu */}
        <button
          type="submit"
          className="w-full bg-gradient-to-r from-pink-500 to-purple-600 text-white py-2 rounded-lg font-bold"
          disabled={uploading}
        >
          {uploading ? 'Yükleniyor...' : 'İçerik Yükle'}
        </button>
      </form>
    </div>
  );
};

export default ContentUploader;