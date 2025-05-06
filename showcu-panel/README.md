# Şovcu Panel | v0.8.0

OnlyVips platformunun içerik üreticileri için tasarlanmış kontrol paneli. İçerik yönetimi, VIP paket oluşturma ve analitik takibi için kullanılır.

## 🌟 Güncellemeler (v0.8.0)

Bu sürümde aşağıdaki önemli güncellemeler ve geliştirmeler yapılmıştır:

- **Backend API Entegrasyonu**: Gerçek veritabanı ve API ile tam entegrasyon
- **TON Connect 2.0**: Gelişmiş blockchain cüzdan bağlantısı ve ödeme sistemi
- **İçerik Yönetim Araçları**: Zenginleştirilmiş içerik oluşturma ve düzenleme özellikleri
- **Analitik Paneli**: Detaylı kullanıcı ve içerik istatistikleri
- **UX/UI İyileştirmeleri**: Daha modern ve kullanıcı dostu arayüz
- **Ödeme Yönetimi**: Otomatik para çekme ve işlem takibi
- **Çoklu Medya Desteği**: Fotoğraf, video ve ses dosyaları için gelişmiş destek
- **Abonelik Raporları**: Gelişmiş abone izleme ve raporlama

## 🚀 Özellikler

- **İçerik Yönetimi**: Fotoğraf, video, ses ve metin içerikleri yükleme ve düzenleme
- **VIP Paket Yönetimi**: Premium içerik paketleri oluşturma ve düzenleme
- **Gelir Takibi**: Aboneler ve gelir istatistikleri
- **Analitik Paneli**: İçerik performansı ve kullanıcı etkileşimi analizi
- **TON Entegrasyonu**: Blockchain ödemeleri ve para çekme
- **Telegram Bağlantısı**: Bot ve Telegram hesap entegrasyonu

## 🛠️ Teknolojiler

- **React**: UI kütüphanesi
- **TypeScript**: Tip güvenliği
- **Vite**: Build aracı
- **Ant Design**: UI komponent kütüphanesi
- **UnoCSS**: Atomik CSS framework
- **TON Connect**: Blockchain cüzdan entegrasyonu
- **Chart.js**: İstatistik ve grafik görselleştirme
- **React Query**: API veri yönetimi ve önbellek

## 📋 Monorepo'da Kullanım

Bu uygulama, monorepo yapısında Yarn Workspaces ile yönetilmektedir. Root dizinden şu şekilde çalıştırabilirsiniz:

```bash
# Geliştirme modunda başlatmak için
yarn start:panel

# Build işlemi için
yarn workspace showcu-panel build
```

## 🚀 Kurulum

### Gereksinimler

- Node.js 16+
- Yarn

### Monorepo Üzerinden Kurulum

1. Bağımlılıkları yükleyin:
   ```bash
   # Root dizinde
   yarn install
   ```

2. `.env` dosyasını oluşturun:
   ```bash
   cd showcu-panel
   cp .env.example .env
   ```

3. `.env` dosyasını düzenleyin:
   ```
   VITE_API_URL=http://localhost:8000
   VITE_TON_NETWORK=testnet
   VITE_TG_WEB_APP_VERSION=6.9
   VITE_MEDIA_URL=http://localhost:8000/media
   ```

4. Geliştirme sunucusunu başlatın:
   ```bash
   # Root dizinde
   yarn start:panel
   
   # Veya showcu-panel dizininde
   yarn dev
   ```

## 📦 Proje Yapısı

```
showcu-panel/
├── public/              # Statik dosyalar
├── src/
│   ├── api/             # API istek fonksiyonları
│   ├── assets/          # Resimler, ikonlar
│   ├── components/      # UI bileşenleri
│   │   ├── content/     # İçerik yönetimi bileşenleri
│   │   └── layout/      # Layout bileşenleri
│   ├── contexts/        # React context'leri
│   ├── hooks/           # Custom React hooks
│   ├── pages/           # Sayfa bileşenleri
│   ├── services/        # Harici servis entegrasyonları
│   ├── styles/          # Stil dosyaları
│   ├── types/           # TypeScript tip tanımları
│   └── utils/           # Yardımcı fonksiyonlar
├── index.html           # HTML şablonu
├── package.json         # Proje ve bağımlılık yapılandırması
├── tsconfig.json        # TypeScript yapılandırması
├── uno.config.ts        # UnoCSS yapılandırması
└── vite.config.ts       # Vite yapılandırması
```

## 🧭 Sayfa Yapısı

Şovcu Panel aşağıdaki ana sayfalardan oluşur:

- **Gösterge Paneli**: Genel bakış ve özet istatistikler
- **İçerik Yönetimi**: İçerik oluşturma, düzenleme ve silme
- **VIP Paketler**: VIP paket yönetimi
- **Aboneler**: Abone listesi ve yönetimi
- **Analitik**: Detaylı performans analizi
- **Cüzdan**: Gelir ve TON para çekme işlemleri
- **Profil**: Profil ayarları ve yapılandırma

## 💎 TON Connect Entegrasyonu

Şovcu Panel, TON blockchain ile entegre çalışarak güvenli ödeme işlemleri sağlar:

```typescript
// TON Connect entegrasyonu
import { TonConnectUI } from '@tonconnect/ui';

// TON cüzdan bağlantısı
const tonConnectUI = new TonConnectUI({
  manifestUrl: 'https://showcu-panel.onlyvips.com/tonconnect-manifest.json',
  buttonRootId: 'ton-connect-button'
});

// Cüzdan bağlandığında
tonConnectUI.onStatusChange(wallet => {
  if (wallet) {
    // Cüzdan bilgilerini kaydet
    setWalletAddress(wallet.account.address);
    
    // Bakiye kontrolü
    fetchBalance(wallet.account.address);
  }
});

// Para çekme işlemi
const withdrawFunds = async (amount) => {
  try {
    const result = await tonConnectUI.sendTransaction({
      validUntil: Math.floor(Date.now() / 1000) + 360,
      messages: [
        {
          address: destinationAddress,
          amount: toNano(amount).toString(),
        }
      ]
    });
    
    // İşlem sonucunu API'ye bildir
    await api.saveTransaction(result.boc);
    
    return result;
  } catch (error) {
    console.error('Para çekme işlemi başarısız:', error);
    throw error;
  }
};
```

## 🔄 Monorepo Entegrasyonu

Bu uygulama, monorepo yapısındaki diğer bileşenlerle aşağıdaki şekilde entegre olur:

1. **Common-Modules**: Ortak tip ve API fonksiyonlarını kullanır
   ```typescript
   import { Content, Package, createContent } from 'onlyvips-common';
   ```

2. **Backend API**: API endpoint'leri ile veri alışverişi yapar

3. **Flirt-Bot**: Telegram üzerinden yönlendirme entegrasyonu

## 📊 Analitik Özellikleri

Analitik paneli, şovcuların içerik performansını izlemeleri için aşağıdaki verileri sunar:

```typescript
import { Chart } from 'chart.js/auto';
import { getAnalytics } from 'onlyvips-common';

// İçerik performans grafiği oluşturma
const renderAnalytics = async () => {
  const { viewsData } = await getAnalytics(contentId);
  
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: viewsData.map(d => d.date),
      datasets: [{
        label: 'Görüntülenme',
        data: viewsData.map(d => d.views)
      }]
    }
  });
};
```

## 🧪 Test

```bash
# Root dizinde
yarn workspace showcu-panel test

# Veya showcu-panel dizininde
yarn test
```

## 🔄 Build ve Dağıtım

```bash
# Build
yarn workspace showcu-panel build

# Önizleme
yarn workspace showcu-panel preview
```

Dağıtım için build klasörü `showcu-panel/dist` dizininde oluşturulur.

## 📄 Lisans

© 2024 SiyahKare. Tüm hakları saklıdır.
