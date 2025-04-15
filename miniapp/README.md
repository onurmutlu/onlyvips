
# 🌟 OnlyVips MiniApp - Telegram İçerik Platformu

OnlyVips MiniApp, Telegram içinde çalışan, içerik üreticileri ve kullanıcılar arasında etkileşim sağlayan premium içerik platformudur.

## 📱 Özellikler

- **Premium İçerik Erişimi**: VIP içeriklere kolayca erişim
- **İçerik Keşfi**: Kategorilere göre içerik keşfetme
- **Şovcu Profilleri**: İçerik üreticilerinin profillerini görüntüleme
- **Görev Sistemi**: XP ve rozet kazanmak için görevleri tamamlama
- **Star Ekonomisi**: Premium içerikler için platform içi ödeme sistemi
- **TON Entegrasyonu**: Kripto para ödemeleri için blockchain desteği
- **Kullanıcı Profili**: XP, seviye ve rozet takibi
- **Abonelik Yönetimi**: VIP paketlere abone olma ve yönetme
- **Telegram Bağlantısı**: Bot ve görev sistemi ile entegrasyon

## 🛠️ Teknolojiler

- React + Vite
- TypeScript
- UnoCSS / TailwindCSS
- React Router
- React Query
- Telegram WebApp SDK
- TON Connect 2.0

## 🚀 Kurulum

```bash
# Gereksinimleri yükle
npm install

# Tip tanımlamalarını yükle
npm i --save-dev @types/react @types/react-router-dom @types/telegram-web-app

# Geliştirme sunucusunu başlat
npm run dev

# Üretim için derleme
npm run build
```

## ⚙️ Ortam Değişkenleri

`.env` dosyasına aşağıdaki değişkenleri ekleyin (örnek `.env.example` dosyasından kopyalayabilirsiniz):

```
VITE_API_URL=https://api.onlyvips.com
VITE_BOT_USERNAME=OnlyVipsBot
```

## 📦 Proje Yapısı

```
miniapp/
├── src/
│   ├── api/           # API istemcisi
│   ├── components/    # UI bileşenleri
│   │   ├── ContentCard.tsx    # İçerik kartı bileşeni
│   │   └── CreatorCard.tsx    # Şovcu kartı bileşeni
│   ├── pages/         # Sayfa bileşenleri
│   │   ├── Home.tsx             # Ana sayfa
│   │   ├── ContentDetail.tsx    # İçerik detay sayfası
│   │   └── CreatorProfile.tsx   # Şovcu profil sayfası
│   ├── types/         # TypeScript tip tanımlamaları
│   │   └── telegram.d.ts        # Telegram WebApp tipleri
│   ├── hooks/         # Özel React hookları
│   ├── utils/         # Yardımcı fonksiyonlar
│   ├── styles/        # CSS stilleri
│   ├── App.tsx        # Ana uygulama bileşeni
│   └── main.tsx       # Uygulama giriş noktası
├── public/            # Statik dosyalar
├── index.html         # HTML şablonu
├── vite.config.ts     # Vite yapılandırması
├── uno.config.ts      # UnoCSS yapılandırması
├── tsconfig.json      # TypeScript yapılandırması
├── package.json       # Proje bağımlılıkları
└── README.md          # Bu dosya
```

## 🔌 API Entegrasyonu

MiniApp, OnlyVips Backend API ile entegre çalışır:

- **İçerik API'leri**: `/content` endpoint'i üzerinden içerik erişimi
- **Şovcu API'leri**: `/creators` endpoint'i üzerinden şovcu bilgileri
- **Kullanıcı API'leri**: `/users` endpoint'i ile kullanıcı profili ve abonelikler
- **Paket API'leri**: `/packages` endpoint'i ile abonelik paketleri
- **Ödeme API'leri**: `/payments` endpoint'i ile TON ödemeleri

## 🖼️ Ana Sayfalar

- **Ana Sayfa**: Öne çıkan içerikler, popüler şovcular ve kategori bazlı keşif
- **İçerik Detay**: İçerik görüntüleme, beğenme ve yorum yapma
- **Şovcu Profili**: Şovcu bilgileri, içerikleri ve abonelik paketleri
- **Kullanıcı Profili**: XP, rozetler ve tamamlanan görevler
- **Görev Sayfası**: Yapılabilecek görevlerin listesi

## 💰 Ödeme Sistemleri

MiniApp, çeşitli ödeme yöntemlerini destekler:

- **TON Blockchain**: Kripto para ödemeleri için entegre edilmiş TON Connect 2.0
- **Star Sistemi**: Premium içerik erişimi için platform içi para birimi
- **VIP Paketler**: Farklı abonelik seviyeleri ve özellikleri

## 🤖 Görev Sistemi

Kullanıcılar aşağıdaki görev tiplerini tamamlayarak XP ve Star kazanabilirler:

- Bot etiketleme
- Kanal/gruba katılma
- İçerik paylaşma
- Mesaj yönlendirme
- Link paylaşma
- Sabitlenmiş mesaj
- Kullanıcı davet etme

## 🌐 Telegram MiniApp Yapılandırması

1. BotFather'a giderek bir bot oluşturun
2. `/newapp` komutuyla yeni bir web uygulaması oluşturun
3. MiniApp URL'ini dağıtım adresiniz olarak ayarlayın (örn. `https://onlyvips.example.com`)
4. Bot üzerinden `/start` komutu ile MiniApp'e erişin

## 📋 Deployment Kontrol Listesi

- [ ] `.env` dosyası düzgün yapılandırıldı
- [ ] API endpoint'leri test edildi
- [ ] Telegram WebApp initData doğrulaması çalışıyor
- [ ] TON Connect entegrasyonu test edildi
- [ ] Statik dosyalar optimize edildi
- [ ] HTTPS yapılandırması tamamlandı
- [ ] Kullanıcı kimliği doğru aktarılıyor
- [ ] Responsive tasarım tüm cihazlarda test edildi

## 🔍 Sorun Giderme

- **"Telegram context bulunamadı"**: MiniApp'in Telegram içinden açıldığından emin olun
- **"API erişim hatası"**: API URL'inin doğru yapılandırıldığını kontrol edin
- **"Kullanıcı kimliği alınamıyor"**: WebApp.initDataUnsafe erişimini kontrol edin
- **"TON ödeme hatası"**: TON cüzdan entegrasyonunu kontrol edin

## 📈 Performans Optimizasyonu

- İçerik resimleri için lazy loading
- API istekleri için önbellek kullanımı
- Chunk loading ile code splitting
- Webpack/Vite optimizasyonları
- React.memo ve useCallback kullanımı

## 📝 Lisans

Tüm hakları saklıdır. SiyahKare tarafından geliştirilmiştir.

## 🔗 İlgili Projeler

- [OnlyVips Flirt Bot](https://github.com/yourusername/onlyvips-flirt-bot) - Telegram Bot
- [OnlyVips Backend](https://github.com/yourusername/onlyvips-backend) - Backend API
- [OnlyVips Showcu Panel](https://github.com/yourusername/onlyvips-showcu-panel) - İçerik Üretici Paneli
