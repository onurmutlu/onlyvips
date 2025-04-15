
# 🌟 Şovcu Panel - OnlyVips İçerik Üretici Platformu

Telegram MiniApp olarak çalışan, içerik oluşturucular (şovcular) için özel olarak geliştirilmiş yönetim paneli.

## 📱 Özellikler

- **İçerik Yönetimi**: Fotoğraf, video, ses ve yazı içeriklerini kolayca yükleyin ve yönetin
- **VIP Paket Oluşturma**: Özel abonelik paketleri oluşturun ve yönetin
- **Analitik Dashboard**: Abone sayısı, görüntülenme ve kazanç istatistiklerini takip edin
- **Gelir Takibi**: TON ödemelerini izleyin ve kazançlarınızı görüntüleyin
- **Abone Yönetimi**: Abonelerinizi ve onların tercihlerini yönetin
- **Telegram Entegrasyonu**: MiniApp API ile tam entegrasyon
- **TON Blockchain Desteği**: Kripto para ödemeleri için TON cüzdan entegrasyonu
- **Çoklu Medya Desteği**: Farklı medya türleri için özel önizlemeler ve oynatıcılar
- **Reaktif Tasarım**: Tüm cihazlarda optimum görüntüleme deneyimi

## 🛠️ Teknolojiler

- React + Vite
- TypeScript
- TailwindCSS
- React Router
- Chart.js (Grafikler için)
- React Query (Veri yönetimi)
- Telegram MiniApp SDK
- TON Connect 2.0 (Blockchain entegrasyonu)

## 🚀 Kurulum

```bash
# Gereksinimleri yükle
npm install

# Tip tanımlamalarını yükle
npm i --save-dev @types/react @types/react-router-dom

# Geliştirme sunucusunu başlat
npm run dev

# Üretim için derleme
npm run build
```

## ⚙️ Ortam Değişkenleri

`.env` dosyasına aşağıdaki değişkenleri ekleyin:

```
# API URL
VITE_API_URL=https://api.onlyvips.com

# Telegram MiniApp
VITE_BOT_USERNAME=OnlyVipsBot

# Medya URL
VITE_MEDIA_URL=https://api.onlyvips.com/uploads

# TON Blockchain Settings
VITE_TON_CENTER=https://toncenter.com/api/v2/jsonRPC
VITE_TON_WALLET_ADDRESS=your_ton_wallet_address
```

## 📦 Proje Yapısı

```
showcu-panel/
├── src/
│   ├── api/           # API istemcisi ve veri işlemleri
│   ├── components/    # Yeniden kullanılabilir UI bileşenleri
│   │   ├── ContentUploader.tsx    # İçerik yükleme bileşeni
│   │   ├── StatisticsPanel.tsx    # İstatistik görüntüleme paneli
│   │   └── PackageManager.tsx     # Paket yönetim bileşeni
│   ├── pages/         # Sayfa bileşenleri
│   ├── types/         # TypeScript tip tanımlamaları
│   ├── hooks/         # Özel React hook'ları
│   ├── utils/         # Yardımcı fonksiyonlar
│   ├── context/       # React context'leri
│   ├── App.tsx        # Ana uygulama bileşeni
│   └── main.tsx       # Uygulama giriş noktası
├── public/            # Statik dosyalar
├── index.html         # HTML şablonu
├── vite.config.ts     # Vite yapılandırması
├── package.json       # Proje bağımlılıkları
└── README.md          # Bu dosya
```

## 🔌 API Entegrasyonu

Şovcu Panel, OnlyVips Backend API ile entegre çalışır:

- **İçerik Yönetimi**: `/creator-panel/content` endpoint'i üzerinden içerik CRUD işlemleri
- **Paket Yönetimi**: `/creator-panel/packages` endpoint'i üzerinden paket CRUD işlemleri
- **İstatistikler**: `/creator-panel/statistics` endpoint'i üzerinden analitik verilere erişim
- **Abone Yönetimi**: `/creator-panel/subscribers` endpoint'i ile abone bilgileri
- **Kazanç Takibi**: `/creator-panel/earnings` endpoint'i ile gelir istatistikleri

## 💰 Ödeme Sistemleri

Şovcu Panel, çeşitli ödeme yöntemlerini destekler:

- **TON Blockchain**: Kripto para ödemeleri için entegre edilmiş TON Connect 2.0
- **Star Sistemi**: Platform içi para birimi olarak Star kullanımı
- **Para Çekme İşlemleri**: Kazançları TON cüzdanına aktarma

## 📊 İçerik Yönetimi Özellikleri

- **Birden Çok Medya Türü**: Fotoğraf, video, ses ve metin içerikleri
- **Premium Fiyatlandırma**: İçerik başına özel fiyatlandırma
- **Zamanlanmış Yayın**: İçerikleri belirli bir tarihte otomatik yayınlama
- **İçerik Etiketleme**: Kategorilendirme ve etiketleme sistemi
- **İstatistik Takibi**: Her içerik için detaylı görüntüleme ve etkileşim analitiği

## 🔐 VIP Paket Yönetimi

- **Özel Paket Oluşturma**: Farklı süreler ve fiyatlar için paket oluşturma
- **Avantaj Tanımlama**: Her pakete özel avantajlar belirleme
- **Abonelik İstatistikleri**: Paket bazlı abonelik analitiği
- **Aktif/Pasif Yapma**: Paketleri satışa açma veya kapatma özelliği

## 📈 Analitik ve İstatistikler

Şovcu Panel, kapsamlı analitik ve performans izleme sunar:

- **Görüntülenme İstatistikleri**: İçerik bazında görüntülenme sayıları
- **Abone Grafiği**: Zaman içinde abone sayısındaki değişimler
- **Gelir Analizi**: Kazanç kaynakları ve toplam gelir
- **Etkileşim Oranları**: Beğeni, yorum ve paylaşım istatistikleri
- **Demografik Veriler**: Abone yaş, cinsiyet ve konum bilgileri

## 🔒 Güvenlik

- **JWT Token Kimlik Doğrulama**: Güvenli API erişimi için JWT kullanımı
- **Telegram Kimlik Doğrulama**: MiniApp üzerinden otomatik kimlik doğrulama
- **Role Dayalı Erişim**: Sadece doğrulanmış şovcular erişebilir
- **Güvenli İçerik Saklama**: İçerikler için güvenli depolama ve erişim yönetimi
- **HTTPS**: Tüm iletişim için şifreli bağlantı

## 🌐 Telegram MiniApp Yapılandırması

1. BotFather'a giderek bir bot oluşturun
2. `/newapp` komutuyla yeni bir web uygulaması oluşturun
3. MiniApp URL'ini projenizin dağıtıldığı URL olarak ayarlayın
4. Bot üzerinden `/start` komutu ile MiniApp'e erişin

## 📋 Deployment Kontrol Listesi

- [ ] `.env` dosyası düzgün yapılandırıldı
- [ ] Telegram Bot yapılandırması tamamlandı
- [ ] API endpoint'leri test edildi
- [ ] TON cüzdan adresi yapılandırıldı
- [ ] Buildpack static hosting için optimize edildi
- [ ] HTTPS sertifikası kuruldu
- [ ] Tüm medya türleri test edildi
- [ ] Responsive tasarım tüm cihazlarda kontrol edildi

## 🔍 Sorun Giderme

- **"API bağlantı hatası"**: API URL'inin doğru olduğundan emin olun
- **"Yükleme yapılamıyor"**: Medya sunucusuna erişim olduğunu kontrol edin
- **"TON bağlantısı kurulamıyor"**: TON cüzdan adresinin doğru olduğunu kontrol edin
- **"Kimlik doğrulama hatası"**: JWT token'ının geçerli olduğunu kontrol edin

## 📝 Lisans

Tüm hakları saklıdır. SiyahKare tarafından geliştirilmiştir.

## 🔗 İlgili Projeler

- [OnlyVips MiniApp](https://github.com/yourusername/onlyvips-miniapp) - Telegram MiniApp
- [OnlyVips Backend](https://github.com/yourusername/onlyvips-backend) - Backend API
- [OnlyVips Flirt Bot](https://github.com/yourusername/onlyvips-flirt-bot) - Telegram Bot
