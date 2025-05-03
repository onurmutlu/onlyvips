# OnlyVips Backend API

OnlyVips platformunun ana API servisidir. Tüm bileşenler (MiniApp, Şovcu Panel ve Flirt-Bot) bu API ile iletişim kurar.

## 🚀 Özellikler

- **Kullanıcı Yönetimi**: Telegram tabanlı kimlik doğrulama ve kullanıcı profil yönetimi
- **İçerik Yönetimi**: Fotoğraf, video ve metin tabanlı içerik oluşturma, düzenleme ve silme
- **VIP Paket Yönetimi**: Premium içerik paketleri oluşturma ve abonelik yönetimi
- **Görev Sistemi**: Kullanıcı görevleri ve ödül mekanizması
- **Cüzdan ve Ödeme**: TON blockchain entegrasyonu ile ödeme işlemleri
- **Analitik**: İçerik performansı ve kullanıcı etkileşim istatistikleri

## 🛠️ Teknolojiler

- **Node.js** ve **Express**: API framework
- **TypeScript**: Tip güvenliği
- **MongoDB**: Veritabanı
- **JWT**: Kimlik doğrulama
- **TON API**: Blockchain entegrasyonu

## 📋 Monorepo'da Kullanım

Bu API, monorepo yapısında Yarn Workspaces ile yönetilmektedir. Root dizinden şu şekilde çalıştırabilirsiniz:

```bash
# Geliştirme modunda başlatmak için
yarn start:backend

# Build işlemi için
yarn workspace onlyvips-backend-api build
```

## 🚀 Kurulum

### Manuel Kurulum

1. Depoyu klonlayın:
   ```bash
   git clone https://github.com/yourusername/onlyvips.git
   ```

2. Bağımlılıkları yükleyin:
   ```bash
   # Root dizinde
   yarn install
   ```

3. `.env` dosyasını oluşturun:
   ```bash
   cd backend-api
   cp .env.example .env
   ```

4. `.env` dosyasını düzenleyin ve gerekli değişkenleri yapılandırın.

5. Veritabanını hazırlayın:
   ```bash
   # MongoDB'yi yerel olarak veya bir sunucuda çalıştırdığınızdan emin olun
   ```

6. Geliştirme sunucusunu başlatın:
   ```bash
   # Root dizinde
   yarn start:backend
   
   # Veya backend-api dizininde
   yarn dev
   ```

### Docker ile Kurulum

1. Docker ve Docker Compose'u yükleyin.

2. `docker-config` dizinindeki `docker-compose.yml` dosyasını düzenleyin ve değişkenleri yapılandırın.

3. Container'ları başlatın:
   ```bash
   cd docker-config
   docker-compose up -d
   ```

## 📚 API Dokümantasyonu

### Kullanıcı ve Kimlik Doğrulama

- `POST /api/auth/telegram`: Telegram kimlik doğrulama
- `GET /api/auth/me`: Geçerli kullanıcı bilgilerini getir
- `GET /api/profile`: Kullanıcı profilini getir
- `GET /api/profile/showcu/:showcuId`: Şovcu profilini getir
- `POST /api/profile/become-showcu`: Şovcu olma başvurusu

### İçerik Yönetimi

- `GET /api/content`: Tüm içerikleri getir
- `GET /api/content/:id`: İçerik detaylarını getir
- `POST /api/content`: Yeni içerik oluştur
- `PUT /api/content/:id`: İçerik güncelle
- `DELETE /api/content/:id`: İçerik sil
- `POST /api/content/:id/like`: İçeriği beğen

### VIP Paket Yönetimi

- `GET /api/packages`: Tüm paketleri getir
- `GET /api/packages/:id`: Paket detaylarını getir
- `POST /api/packages`: Yeni paket oluştur
- `PUT /api/packages/:id`: Paket güncelle
- `DELETE /api/packages/:id`: Paket sil
- `POST /api/packages/:id/subscribe`: Pakete abone ol
- `GET /api/packages/subscriptions/list`: Tüm abonelikleri getir

### Görev Sistemi

- `GET /api/tasks`: Görevleri listele
- `POST /api/tasks/complete`: Görev tamamla

### Cüzdan ve Ödeme

- `GET /api/wallet`: Cüzdan bilgilerini getir
- `PUT /api/wallet/ton-address`: TON adresi güncelle
- `POST /api/wallet/withdraw`: Para çekme talebi oluştur
- `POST /api/wallet/purchase-stars`: Star satın al

### Analitik

- `GET /api/analytics/dashboard`: Şovcu gösterge paneli
- `GET /api/analytics/content/:id`: İçerik analitiği
- `GET /api/analytics/package/:id`: Paket analitiği

## 🔄 Monorepo Entegrasyonu

Bu API, `common-modules` paketini kullanarak tipler ve yardımcı işlevleri paylaşır:

```typescript
import { User, Content } from 'onlyvips-common';

// Modellerde ve route'larda 
```

### TypeScript Özel Tiplerini Kullanma

Model tanımlarınızı iyileştirmek için ortak tipleri kullanın:

```typescript
import { User } from 'onlyvips-common';

// User modelini ortak tiplerle genişletme
export interface IUserDocument extends User, Document {
  // Veritabanı spesifik alanlar
}
```

## 🔗 Diğer Bileşenlerle Entegrasyon

- **MiniApp**: REST API üzerinden JSON veri alışverişi
- **Şovcu Panel**: REST API üzerinden içerik yönetimi
- **Flirt-Bot**: Bot doğrulama ve görev tamamlama entegrasyonu

## 🧪 Test

```bash
# Root dizinde
yarn workspace onlyvips-backend-api test

# Veya backend-api dizininde
yarn test
```

## 📄 Lisans

© 2024 SiyahKare. Tüm hakları saklıdır.

