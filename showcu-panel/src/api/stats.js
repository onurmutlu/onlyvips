import apiClient from './client';

/**
 * Dashboard istatistiklerini getirir
 */
export const getDashboardStats = async () => {
  try {
    const response = await apiClient.get('/stats/dashboard');
    return response.data;
  } catch (error) {
    console.error('Dashboard istatistikleri hatası:', error);
    throw error;
  }
};

/**
 * Gelir istatistiklerini getirir
 * @param {string} period - Periyot (week, month, year, all)
 */
export const getRevenue = async (period = 'month') => {
  try {
    const response = await apiClient.get(`/stats/revenue?period=${period}`);
    return response.data;
  } catch (error) {
    console.error('Gelir istatistikleri hatası:', error);
    throw error;
  }
};

/**
 * İçerik görüntülenme istatistiklerini getirir
 * @param {string} period - Periyot (week, month, year, all)
 */
export const getViews = async (period = 'month') => {
  try {
    const response = await apiClient.get(`/stats/views?period=${period}`);
    return response.data;
  } catch (error) {
    console.error('Görüntülenme istatistikleri hatası:', error);
    throw error;
  }
};

/**
 * En çok gelir getiren içerikler
 * @param {number} limit - Maksimum içerik sayısı
 */
export const getTopContents = async (limit = 5) => {
  try {
    const response = await apiClient.get(`/stats/top-contents?limit=${limit}`);
    return response.data;
  } catch (error) {
    console.error('En çok kazandıran içerik hatası:', error);
    throw error;
  }
};

/**
 * Kategoriye göre içerik dağılımı
 */
export const getCategoryDistribution = async () => {
  try {
    const response = await apiClient.get('/stats/categories');
    return response.data;
  } catch (error) {
    console.error('Kategori dağılımı hatası:', error);
    throw error;
  }
};

/**
 * Abone kullanıcı istatistikleri
 */
export const getSubscriberStats = async () => {
  try {
    const response = await apiClient.get('/stats/subscribers');
    return response.data;
  } catch (error) {
    console.error('Abone istatistikleri hatası:', error);
    throw error;
  }
}; 