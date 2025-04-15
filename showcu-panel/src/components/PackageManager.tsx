// showcu-panel/src/components/PackageManager.tsx
import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import api from '../api/creatorApi';

interface Package {
  id: string;
  name: string;
  description: string;
  price: number;
  duration: number; // ay cinsinden
  benefits: string[];
  isActive: boolean;
  subscriberCount: number;
  createdAt: string;
}

interface PackageFormData {
  name: string;
  description: string;
  price: number;
  duration: number;
  benefits: string;
  isActive: boolean;
}

const PackageManager: React.FC = () => {
  const [packages, setPackages] = useState<Package[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  
  const { register, handleSubmit, reset, setValue, formState: { errors } } = useForm<PackageFormData>();
  
  useEffect(() => {
    loadPackages();
  }, []);
  
  const loadPackages = async () => {
    try {
      setLoading(true);
      const response = await api.getCreatorPackages();
      
      if (response.success) {
        setPackages(response.data.packages);
      }
    } catch (error) {
      console.error('Paket yükleme hatası:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleEdit = (packageItem: Package) => {
    setEditing(packageItem.id);
    setValue('name', packageItem.name);
    setValue('description', packageItem.description);
    setValue('price', packageItem.price);
    setValue('duration', packageItem.duration);
    setValue('benefits', packageItem.benefits.join('\n'));
    setValue('isActive', packageItem.isActive);
  };
  
  const handleCreate = () => {
    setIsCreating(true);
    reset({
      name: '',
      description: '',
      price: 50,
      duration: 1,
      benefits: '',
      isActive: true
    });
  };
  
  const handleCancel = () => {
    setEditing(null);
    setIsCreating(false);
  };
  
  const onSubmit = async (data: PackageFormData) => {
    try {
      const processedData = {
        ...data,
        benefits: data.benefits.split('\n').filter(b => b.trim() !== '')
      };
      
      let response;
      
      if (isCreating) {
        response = await api.createPackage(processedData);
      } else if (editing) {
        response = await api.updatePackage(editing, processedData);
      }
      
      if (response && response.success) {
        setEditing(null);
        setIsCreating(false);
        loadPackages();
      } else {
        alert(`Hata: ${response?.error || 'Paket kaydedilemedi'}`);
      }
    } catch (error) {
      console.error('Paket kaydetme hatası:', error);
      alert('Paket kaydedilirken bir hata oluştu');
    }
  };
  
  const handleDelete = async (packageId: string) => {
    if (!confirm('Bu paketi silmek istediğinizden emin misiniz?')) {
      return;
    }
    
    try {
      const response = await api.deletePackage(packageId);
      
      if (response.success) {
        loadPackages();
      } else {
        alert(`Hata: ${response.error}`);
      }
    } catch (error) {
      console.error('Paket silme hatası:', error);
      alert('Paket silinirken bir hata oluştu');
    }
  };
  
  if (loading && packages.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-xl text-pink-500 animate-pulse">Paketler yükleniyor...</div>
      </div>
    );
  }
  
  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-white">VIP Paketler</h2>
        
        {!isCreating && !editing && (
          <button
            className="bg-pink-500 text-white px-4 py-2 rounded-lg"
            onClick={handleCreate}
          >
            Yeni Paket Ekle
          </button>
        )}
      </div>
      
      {(isCreating || editing) ? (
        <form onSubmit={handleSubmit(onSubmit)} className="bg-gray-700 rounded-lg p-4 mb-6">
          <h3 className="text-xl font-bold text-white mb-4">
            {isCreating ? 'Yeni Paket Oluştur' : 'Paketi Düzenle'}
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-white mb-2">Paket Adı</label>
              <input
                type="text"
                className="w-full p-2 bg-gray-600 text-white rounded-lg"
                {...register('name', { required: true })}
              />
              {errors.name && <span className="text-red-500">Paket adı gerekli</span>}
            </div>
            
            <div>
              <label className="block text-white mb-2">Fiyat (Star)</label>
              <input
                type="number"
                className="w-full p-2 bg-gray-600 text-white rounded-lg"
                {...register('price', { required: true, min: 1 })}
              />
              {errors.price && <span className="text-red-500">Geçerli bir fiyat girin</span>}
            </div>
          </div>
          
          <div className="mb-4">
            <label className="block text-white mb-2">Açıklama</label>
            <textarea
              className="w-full p-2 bg-gray-600 text-white rounded-lg"
              rows={3}
              {...register('description', { required: true })}
            />
            {errors.description && <span className="text-red-500">Açıklama gerekli</span>}
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-white mb-2">Süre (Ay)</label>
              <input
                type="number"
                className="w-full p-2 bg-gray-600 text-white rounded-lg"
                {...register('duration', { required: true, min: 1 })}
              />
              {errors.duration && <span className="text-red-500">Geçerli bir süre girin</span>}
            </div>
            
            <div>
              <label className="block text-white mb-2">Aktif</label>
              <div className="p-2">
                <input 
                  type="checkbox" 
                  className="mr-2" 
                  {...register('isActive')} 
                />
                <span className="text-white">Bu paket satışa açık</span>
              </div>
            </div>
          </div>
          
          <div className="mb-4">
            <label className="block text-white mb-2">Avantajlar (Her satır bir madde)</label>
            <textarea
              className="w-full p-2 bg-gray-600 text-white rounded-lg"
              rows={5}
              placeholder="Örn: Tüm içeriklere erişim&#10;Özel içerikler&#10;Haftalık flört ipuçları"
              {...register('benefits', { required: true })}
            />
            {errors.benefits && <span className="text-red-500">En az bir avantaj ekleyin</span>}
          </div>
          
          <div className="flex justify-end space-x-4">
            <button
              type="button"
              className="bg-gray-500 text-white px-4 py-2 rounded-lg"
              onClick={handleCancel}
            >
              İptal
            </button>
            <button
              type="submit"
              className="bg-pink-500 text-white px-4 py-2 rounded-lg"
            >
              {isCreating ? 'Oluştur' : 'Kaydet'}
            </button>
          </div>
        </form>
      ) : packages.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {packages.map(packageItem => (
            <div 
              key={packageItem.id} 
              className={`bg-gray-700 rounded-lg p-4 border ${
                packageItem.isActive ? 'border-green-500' : 'border-gray-600'
              }`}
            >
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-xl font-bold text-white">{packageItem.name}</h3>
                <div className="flex space-x-2">
                  <button
                    className="text-blue-400 hover:text-blue-300"
                    onClick={() => handleEdit(packageItem)}
                  >
                    Düzenle
                  </button>
                  <button
                    className="text-red-400 hover:text-red-300"
                    onClick={() => handleDelete(packageItem.id)}
                  >
                    Sil
                  </button>
                </div>
              </div>
              
              <p className="text-gray-300 mb-4">{packageItem.description}</p>
              
              <div className="flex justify-between items-center mb-4">
                <div>
                  <span className="text-2xl font-bold text-pink-400">{packageItem.price}</span>
                  <span className="text-pink-300"> Star</span>
                </div>
                <div className="text-gray-300">
                  {packageItem.duration} {packageItem.duration === 1 ? 'ay' : 'ay'}
                </div>
              </div>
              
              <ul className="mb-4">
                {packageItem.benefits.map((benefit, index) => (
                  <li key={index} className="flex items-start mb-2">
                    <span className="text-green-400 mr-2">✓</span>
                    <span className="text-gray-200">{benefit}</span>
                  </li>
                ))}
              </ul>
              
              <div className="flex justify-between items-center text-sm text-gray-400 mt-4">
                <div>{packageItem.subscriberCount} abone</div>
                <div>{new Date(packageItem.createdAt).toLocaleDateString('tr-TR')}</div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-gray-700 rounded-lg p-8 text-center">
          <p className="text-gray-300 mb-4">Henüz hiç VIP paketiniz yok.</p>
          <button
            className="bg-pink-500 text-white px-4 py-2 rounded-lg"
            onClick={handleCreate}
          >
            İlk Paketini Oluştur
          </button>
        </div>
      )}
    </div>
  );
};

export default PackageManager;