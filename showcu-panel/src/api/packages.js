import apiClient from './client';

/**
 * Showcu'nun tüm VIP paketlerini getirir
 */
export const getPackages = async () => {
  try {
    const response = await apiClient.get('/packages/my');
    return response.data;
  } catch (error) {
    console.error('Paket getirme hatası:', error);
    throw error;
  }
};

/**
 * Paket detayını ID'ye göre getirir
 */
export const getPackageById = async (packageId) => {
  try {
    const response = await apiClient.get(`/packages/${packageId}`);
    return response.data;
  } catch (error) {
    console.error('Paket detay hatası:', error);
    throw error;
  }
};

/**
 * Yeni VIP paketi oluşturur
 * @param {Object} packageData - Paket verileri
 * @param {string} packageData.title - Paket başlığı
 * @param {string} packageData.description - Paket açıklaması
 * @param {number} packageData.price - Fiyat (TON biriminde)
 * @param {number} packageData.duration - Gün cinsinden süre
 * @param {Array} packageData.content_ids - İçerik ID'leri
 * @param {boolean} packageData.badge_reward - Rozet ödülü var mı?
 * @param {string} packageData.badge_name - Rozet adı
 */
export const createPackage = async (packageData) => {
  try {
    const response = await apiClient.post('/packages', packageData);
    return response.data;
  } catch (error) {
    console.error('Paket oluşturma hatası:', error);
    throw error;
  }
};

/**
 * VIP paketi günceller
 */
export const updatePackage = async (packageId, packageData) => {
  try {
    const response = await apiClient.put(`/packages/${packageId}`, packageData);
    return response.data;
  } catch (error) {
    console.error('Paket güncelleme hatası:', error);
    throw error;
  }
};

/**
 * VIP paketi siler
 */
export const deletePackage = async (packageId) => {
  try {
    const response = await apiClient.delete(`/packages/${packageId}`);
    return response.data;
  } catch (error) {
    console.error('Paket silme hatası:', error);
    throw error;
  }
};

/**
 * Paket abonesi kullanıcı listesi
 */
export const getPackageSubscribers = async (packageId) => {
  try {
    const response = await apiClient.get(`/packages/${packageId}/subscribers`);
    return response.data;
  } catch (error) {
    console.error('Paket aboneleri getirme hatası:', error);
    throw error;
  }
};

/**
 * Paket istatistikleri
 */
export const getPackageStats = async (packageId) => {
  try {
    const response = await apiClient.get(`/packages/${packageId}/stats`);
    return response.data;
  } catch (error) {
    console.error('Paket istatistiği hatası:', error);
    throw error;
  }
}; 