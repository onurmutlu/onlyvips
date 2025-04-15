import apiClient from './client';

/**
 * Showcu'nun tüm içeriklerini getirir
 */
export const getContents = async () => {
  try {
    const response = await apiClient.get('/contents/my');
    return response.data;
  } catch (error) {
    console.error('İçerik getirme hatası:', error);
    throw error;
  }
};

/**
 * İçerik detayını ID'ye göre getirir
 */
export const getContentById = async (contentId) => {
  try {
    const response = await apiClient.get(`/contents/${contentId}`);
    return response.data;
  } catch (error) {
    console.error('İçerik detay hatası:', error);
    throw error;
  }
};

/**
 * Yeni içerik yükler (multipart/form-data)
 */
export const uploadContent = async (contentData, file) => {
  const formData = new FormData();
  
  // Dosyayı ekle
  formData.append('file', file);
  
  // İçerik verilerini ekle
  Object.keys(contentData).forEach(key => {
    // Dizileri JSON olarak ekle
    if (Array.isArray(contentData[key])) {
      formData.append(key, JSON.stringify(contentData[key]));
    } else {
      formData.append(key, contentData[key]);
    }
  });
  
  try {
    const response = await apiClient.post('/contents', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('İçerik yükleme hatası:', error);
    throw error;
  }
};

/**
 * İçerik güncelleme (dosya olmadan)
 */
export const updateContent = async (contentId, contentData) => {
  try {
    const response = await apiClient.put(`/contents/${contentId}`, contentData);
    return response.data;
  } catch (error) {
    console.error('İçerik güncelleme hatası:', error);
    throw error;
  }
};

/**
 * İçerik medyasını güncelleme
 */
export const updateContentMedia = async (contentId, file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await apiClient.post(`/contents/${contentId}/media`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('İçerik medya güncelleme hatası:', error);
    throw error;
  }
};

/**
 * İçerik silme
 */
export const deleteContent = async (contentId) => {
  try {
    const response = await apiClient.delete(`/contents/${contentId}`);
    return response.data;
  } catch (error) {
    console.error('İçerik silme hatası:', error);
    throw error;
  }
};

/**
 * Kategori listesi
 */
export const getCategories = async () => {
  try {
    const response = await apiClient.get('/contents/categories');
    return response.data;
  } catch (error) {
    console.error('Kategori getirme hatası:', error);
    throw error;
  }
};

/**
 * İçerik istatistikleri getirme
 */
export const getContentStats = async (contentId) => {
  try {
    const response = await apiClient.get(`/contents/${contentId}/stats`);
    return response.data;
  } catch (error) {
    console.error('İçerik istatistiği hatası:', error);
    throw error;
  }
}; 