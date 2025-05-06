# OnlyVips MiniApp | v0.8.0

Telegram Mini App kullanıcı arayüzü.

## 📋 İçindekiler

- [Genel Bakış](#genel-bakış)
- [Kurulum](#kurulum)
- [Geliştirme](#geliştirme)
- [Ortam Değişkenleri](#ortam-değişkenleri)
- [Vercel Secrets Yönetimi](#vercel-secrets-yönetimi)
- [Yapı ve Mimarisi](#yapı-ve-mimarisi)
- [Telegram Mini App Entegrasyonu](#telegram-mini-app-entegrasyonu)
- [TON Cüzdan Entegrasyonu](#ton-cüzdan-entegrasyonu)
- [Testler](#testler)
- [Dağıtım](#dağıtım)

## 🔍 Genel Bakış

OnlyVips MiniApp, kullanıcıların Telegram üzerinden platformla etkileşime girmelerini sağlayan bir Telegram Mini App'tir. React ve Vite kullanılarak geliştirilmiştir.

## 🌟 Güncellemeler (v0.8.0)

Bu sürümde aşağıdaki önemli güncellemeler ve geliştirmeler yapılmıştır:

- **Backend API Entegrasyonu**: Gerçek API ile tam entegrasyon
- **TON Connect 2.0**: Blockchain cüzdan bağlantısı ve ödeme altyapısı
- **UX İyileştirmeleri**: Kullanıcı deneyimi optimize edildi
- **Vercel Dağıtım Yapılandırması**: CI/CD pipeline kurulumu
- **Güvenli Secret Yönetimi**: Hassas bilgiler için Vercel Secrets kullanımı
- **Görev Sistemi Entegrasyonu**: API ile görev tamamlama akışı
- **Kullanıcı Profil Sayfası**: Detaylı profil görüntüleme ve düzenleme
- **İçerik Vitrin Sayfaları**: Premium içerik erişimi ve görüntülemesi

## 🚀 Kurulum

### Gereksinimler

- Node.js 16+
- Yarn veya npm

### Bağımlılıkları Yükleme

```bash
# Proje klasörüne git
cd miniapp

# Bağımlılıkları yükle
yarn install
```

## 💻 Geliştirme

### Geliştirme Sunucusu Başlatma

```bash
yarn dev
```

Uygulama http://localhost:5173 adresinde erişilebilir olacaktır.

### Build Alma

```bash
yarn build
```

## 🔐 Ortam Değişkenleri

MiniApp, çeşitli yapılandırmalar için ortam değişkenlerini kullanır. Geliştirme için, `.env.example` dosyasını `.env` olarak kopyalayın ve gerekli değerleri güncelleyin:

```env
VITE_API_URL=http://localhost:8000
VITE_TELEGRAM_BOT_USERNAME=YourBotUsername
VITE_TG_WEB_APP_VERSION=6.9
VITE_TON_NETWORK=testnet
VITE_MEDIA_URL=http://localhost:8000/media
```

## 🔑 Vercel Secrets Yönetimi

Üretim ortamında, ortam değişkenleri yerine Vercel Secrets kullanılmaktadır. Bu sayede hassas bilgiler güvenli bir şekilde saklanır ve kod tabanına eklenmez.

### Vercel CLI ile Secret Ekleme

```bash
# Vercel CLI'ı yükleyin
npm install -g vercel

# Projeye giriş yapın
vercel login
vercel link

# Secret ekleyin
vercel secrets add VITE_API_URL https://api.onlyvips.com
vercel secrets add VITE_TELEGRAM_BOT_USERNAME OnlyVipsProdBot
```

### Vercel Dashboard ile Secret Ekleme

1. [Vercel Dashboard](https://vercel.com)'a giriş yapın
2. Proje sayfasına gidin
3. "Settings" > "Environment Variables" bölümüne gidin
4. Gerekli değişkenleri ekleyin:
   - `VITE_API_URL`
   - `VITE_TELEGRAM_BOT_USERNAME`
   - `VITE_TG_WEB_APP_VERSION`
   - `VITE_TON_NETWORK`
   - `VITE_MEDIA_URL`

Bu değişkenler, build sırasında kod tabanına eklenir ve uygulamanızın yapılandırılmasını sağlar.

## 📂 Yapı ve Mimarisi

```
miniapp/
├── public/           # Statik dosyalar
├── src/
│   ├── api/          # API istek fonksiyonları
│   ├── components/   # React bileşenleri
│   ├── hooks/        # Özel React hooks
│   ├── pages/        # Sayfa bileşenleri
│   ├── styles/       # CSS dosyaları
│   ├── types/        # TypeScript tiplemeleri
│   ├── utils/        # Yardımcı fonksiyonlar
│   ├── App.tsx       # Ana uygulama bileşeni
│   └── main.tsx      # Giriş noktası
├── tests/
│   ├── unit/         # Birim testleri
│   └── e2e/          # End-to-end testleri
├── .env.example      # Örnek ortam değişkenleri
├── vite.config.ts    # Vite yapılandırması
└── tsconfig.json     # TypeScript yapılandırması
```

## 🔗 Telegram Mini App Entegrasyonu

MiniApp, Telegram Mini App API'sini kullanarak Telegram ile entegre olur. Telegram Mini App'in sağladığı WebApp nesnesine `window.Telegram.WebApp` üzerinden erişilebilir.

### Önemli Entegrasyon Noktaları

- Web App Başlatma
- Telegram Kullanıcı Bilgilerine Erişim
- Telegram Ana Tema Renklerini Kullanma
- Telegram UI Öğelerini Kullanma (MainButton, BackButton vb.)

## 💎 TON Cüzdan Entegrasyonu

MiniApp, TON Connect 2.0 kullanarak TON blockchain cüzdanlarıyla entegre olur. Bu entegrasyon şu özellikleri sağlar:

- Cüzdan Bağlantısı
- TON Token Transferleri
- İşlem İmzalama
- Bakiye Görüntüleme

```typescript
// Örnek TON cüzdan bağlantısı
import { TonConnectUI } from '@tonconnect/ui';

// TON Connect UI başlatma
const tonConnectUI = new TonConnectUI({
  manifestUrl: 'https://onlyvips.com/tonconnect-manifest.json',
  buttonRootId: 'ton-connect-button'
});

// Cüzdan durumunu dinleme
tonConnectUI.onStatusChange(wallet => {
  if (wallet) {
    console.log('Cüzdan bağlandı:', wallet.account.address);
  } else {
    console.log('Cüzdan bağlantısı kesildi');
  }
});
```

## 🧪 Testler

### Birim Testleri Çalıştırma

```bash
yarn test
```

### E2E Testleri Çalıştırma

```bash
yarn test:e2e
```

## 📦 Dağıtım

Uygulama Vercel üzerinde host edilmektedir. Dağıtım işlemi, GitHub repository'sine bir değişiklik push edildiğinde CI/CD pipeline tarafından otomatik olarak gerçekleştirilir.

Eğer manuel olarak dağıtım yapmak istiyorsanız:

```bash
# Vercel CLI ile
vercel

# Üretim için
vercel --prod
```

---

© 2024 SiyahKare. Tüm hakları saklıdır.
