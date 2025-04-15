import apiClient from './client';

/**
 * Kullanıcı profilini getirir
 */
export const getProfile = async () => {
  try {
    const response = await apiClient.get('/users/profile');
    return response.data;
  } catch (error) {
    console.error('Profil getirme hatası:', error);
    throw error;
  }
};

/**
 * Profil güncelleme
 * @param {Object} profileData - Profil verileri
 */
export const updateProfile = async (profileData) => {
  try {
    const response = await apiClient.put('/users/profile', profileData);
    return response.data;
  } catch (error) {
    console.error('Profil güncelleme hatası:', error);
    throw error;
  }
};

/**
 * Profil fotoğrafı güncelleme
 * @param {File} file - Profil fotoğrafı dosyası
 */
export const updateAvatar = async (file) => {
  const formData = new FormData();
  formData.append('avatar', file);
  
  try {
    const response = await apiClient.post('/users/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Avatar güncelleme hatası:', error);
    throw error;
  }
};

/**
 * Kapak fotoğrafı güncelleme
 * @param {File} file - Kapak fotoğrafı dosyası
 */
export const updateCoverPhoto = async (file) => {
  const formData = new FormData();
  formData.append('cover', file);
  
  try {
    const response = await apiClient.post('/users/cover', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Kapak fotoğrafı güncelleme hatası:', error);
    throw error;
  }
};

/**
 * Sosyal medya bağlantılarını güncelleme
 * @param {Object} socialLinks - Sosyal medya bağlantıları
 */
export const updateSocialLinks = async (socialLinks) => {
  try {
    const response = await apiClient.put('/users/social', { social_links: socialLinks });
    return response.data;
  } catch (error) {
    console.error('Sosyal medya güncelleme hatası:', error);
    throw error;
  }
};

/**
 * Showcu kategorilerini güncelleme
 * @param {Array} categories - Kategori listesi
 */
export const updateCategories = async (categories) => {
  try {
    const response = await apiClient.put('/users/categories', { categories });
    return response.data;
  } catch (error) {
    console.error('Kategori güncelleme hatası:', error);
    throw error;
  }
};

/**
 * Bildirim ayarlarını güncelleme
 * @param {Object} notificationSettings - Bildirim ayarları
 */
export const updateNotificationSettings = async (notificationSettings) => {
  try {
    const response = await apiClient.put('/users/notifications', notificationSettings);
    return response.data;
  } catch (error) {
    console.error('Bildirim ayarları güncelleme hatası:', error);
    throw error;
  }
}; 