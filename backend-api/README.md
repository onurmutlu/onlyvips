# OnlyVips Backend API | v0.8.0

OnlyVips ekosisteminin ana backend API bileşenidir. Kullanıcı yönetimi, içerik servisi, görev takibi, ödeme işlemleri ve yapay zeka entegrasyonlarını sağlar.

## Geliştirme Durumu

### Tamamlanan Bileşenler ✅

- **Ana API Yapısı**: FastAPI tabanlı ana mimari kurulumu
- **Temel Endpoint'ler**: Kullanıcı, içerik ve görev endpoint'leri
- **Görev Yönetimi**: Görev oluşturma, listeleme, tamamlama ve doğrulama
- **Metrik ve Loglama**: API kullanım metrikleri
- **Kimlik Doğrulama**: JWT tabanlı yetkilendirme sistemi 
- **CORS Desteği**: Crossorigin istekleri için CORS desteği
- **Yapay Zeka API'leri**: GPT entegrasyonu için endpoint'ler
- **Veritabanı Entegrasyonu**: MongoDB desteği ve veritabanı soyutlama katmanı
- **Rol Tabanlı Yetkilendirme**: Farklı kullanıcı rolleri ve izin sistemi
- **Telegram Auth**: Telegram ile kimlik doğrulama entegrasyonu
- **API Key Auth**: Servisler arası iletişim için API Key doğrulama sistemi

### Yeni Eklenen Özellikler (v0.8.0) 🔥

- **Veritabanı Soyutlama**: `DatabaseInterface` üzerinden çoklu veritabanı desteği
- **MongoDB Entegrasyonu**: Üretim için MongoDB desteği (MemoryDB'den geçiş)
- **JWT Token Sistemi**: Gelişmiş JWT tabanlı kimlik doğrulama
- **Rol ve İzin Sistemi**: Detaylı yetkilendirme mekanizması
- **Telegram Auth Entegrasyonu**: Telegram ile seamless kimlik doğrulama
- **Docker Entegrasyonu**: Geliştirme ve üretim için Docker yapılandırması
- **Kullanıcı Profil Sistemi**: Kullanıcı profillerinin yönetimi

### Görev Sistemi Özellikleri 🚀

Tüm gerekli görev tipleri için endpoint'ler eklendi:

1. **Görev Listeleme**: Tüm mevcut görevleri getirme 
2. **Kullanıcı Görevleri**: Belirli bir kullanıcının görevlerini ve durumlarını getirme
3. **Görev Tamamlama**: Kullanıcıların görev tamamlamasını bildirme
4. **Görev Doğrulama**: Bot veya admin tarafından görev doğrulama 
5. **Bekleyen Görevler**: Admin panel için doğrulama bekleyen görevleri listeleme
6. **Günlük Limit Sıfırlama**: Görevlerin günlük deneme limitlerini sıfırlama
7. **Rozet Atama**: Kullanıcılara rozet atama

### Desteklenen Görev Tipleri 📋

- `start_command`: Telegram botunu başlatma görevi
- `join_channel`: Telegram kanalına katılma görevi 
- `emoji_reaction`: Kanaldaki mesaja emoji tepkisi verme
- `group_join_message`: Gruba katılıp mesaj gönderme
- `inline_button_click`: Inline butona tıklama
- `forward_message`: Mesaj iletme
- `button_click`: Buton tıklama
- `voting`: Ankete katılma
- `schedule_post`: Zamanlanmış mesaj

## Entegrasyonlar 🔌

- **Flirt-Bot**: Bot görev doğrulama ve bildirim sistemi
- **MiniApp**: Telegram MiniApp için API erişimi 
- **Showcu Panel**: Yönetim paneli ile entegrasyon
- **MongoDB**: Veritabanı entegrasyonu
- **JWT**: Kimlik doğrulama için JWT entegrasyonu

## Veritabanı Desteği 🗄️

API aşağıdaki veritabanı sağlayıcılarını destekler:

1. **Memory Database**: Geliştirme için bellek içi veritabanı (varsayılan)
2. **MongoDB**: Üretim ortamı için MongoDB desteği

Veritabanı sağlayıcısını `.env` dosyasında ayarlayabilirsiniz:

```env
# Memory DB kullanmak için
DB_PROVIDER=memory

# MongoDB kullanmak için
DB_PROVIDER=mongodb
DB_HOST=localhost
DB_PORT=27017
DB_USER=onlyvips
DB_PASSWORD=your_secure_password
DB_NAME=onlyvips
```

## Kimlik Doğrulama ve Yetkilendirme 🔐

Backend API, aşağıdaki kimlik doğrulama yöntemlerini destekler:

1. **JWT Token**: Kullanıcı kimlik doğrulaması için
2. **API Key**: Servisler arası iletişim için
3. **Telegram Auth**: Telegram kullanıcıları için doğrulama

Rol tabanlı yetkilendirme sistemi aşağıdaki rolleri içerir:

- `admin`: Tüm izinlere sahip
- `showcu`: İçerik ve paket yönetimi
- `moderator`: İçerik ve görev doğrulama
- `user`: Standart kullanıcı
- `system`: Sistem servisleri

## Yapılacak İşler 🔍

1. **API Dokümantasyonu**: Daha kapsamlı API dokümantasyonu
2. **Test Kapsamı**: Endpoint'ler için birim ve entegrasyon testleri
3. **Rate Limiting**: Hız sınırlama mekanizması
4. **Görev Filtreleme**: Kullanıcıya özel görev filtreleme ve önceliklendirme 

## Kurulum ve Çalıştırma 🔧

```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# Uygulamayı çalıştır
uvicorn main:app --reload
```

## API Dokümantasyonu 📚

API dokümantasyonuna aşağıdaki URL'lerden erişilebilir:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Docker ile Çalıştırma 🐳

```bash
# Docker image oluştur
docker build -t onlyvips-backend-api .

# Container başlat
docker run -p 8000:8000 --env-file .env onlyvips-backend-api
```

## 🚀 Özellikler

- **Kullanıcı Yönetimi**: Telegram tabanlı kimlik doğrulama ve kullanıcı profil yönetimi
- **İçerik Yönetimi**: Fotoğraf, video ve metin tabanlı içerik oluşturma, düzenleme ve silme
- **VIP Paket Yönetimi**: Premium içerik paketleri oluşturma ve abonelik yönetimi
- **Görev Sistemi**: Kullanıcı görevleri ve ödül mekanizması
- **Cüzdan ve Ödeme**: TON blockchain entegrasyonu ile ödeme işlemleri
- **Analitik**: İçerik performansı ve kullanıcı etkileşim istatistikleri

## 🛠️ Teknolojiler

- **FastAPI**: API framework
- **Pydantic**: Veri doğrulama
- **MongoDB**: Veritabanı
- **JWT**: Kimlik doğrulama
- **Docker**: Konteynerizasyon

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

