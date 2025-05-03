// Tarih formatları ve dönüşümler için yardımcı fonksiyonlar
export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('tr-TR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

// Fiyat formatı için yardımcı fonksiyon
export const formatPrice = (price: number): string => {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
  }).format(price);
};

// Kullanıcı seviyesi hesaplama
export const calculateUserLevel = (xp: number): number => {
  return Math.floor(xp / 100) + 1;
};

// Medya türüne göre ikon belirleme
export const getMediaTypeIcon = (mediaType: string): string => {
  switch (mediaType) {
    case 'image':
      return '📷';
    case 'video':
      return '🎬';
    case 'audio':
      return '🎵';
    case 'text':
      return '📝';
    case 'collection':
      return '📚';
    default:
      return '📄';
  }
}; 