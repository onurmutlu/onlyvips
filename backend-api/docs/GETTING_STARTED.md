# OnlyVips Backend API: Başlangıç Kılavuzu

Bu belge, OnlyVips backend API'sini başlatmak, yapılandırmak ve kullanmak için gereken adımları içerir.

## 🚀 Kurulum

### Önkoşullar

- Node.js 16+ yüklü olmalı
- MongoDB 5+ kurulu olmalı (yerel veya uzak bağlantı)
- Yarn paket yöneticisi
- Poetry (Python paketleri için)

### Monorepo Üzerinden Kurulum

1. Kök dizindeki kurulum script'ini kullanın:

```bash
# Projenin kök dizininde
chmod +x install.sh
./install.sh
```

Bu komut, tüm JavaScript ve Python bağımlılıklarını otomatik olarak yükleyecektir.

2. `.env` dosyasını oluşturun:

```bash
cd backend-api
cp .env.example .env
```

3. Dosyayı düzenleyerek gerekli değişkenleri ayarlayın:

```
# MongoDB bağlantı URL'si
MONGODB_URI=mongodb://localhost:27017/onlyvips

# JWT kimlik doğrulama için gizli anahtar (güçlü bir değer kullanın)
JWT_SECRET=your_secure_random_string_here
JWT_EXPIRES_IN=30d

# CORS için izin verilen kaynaklar
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Manuel Kurulum

Alternatif olarak, backend API'yi tek başına kurabilirsiniz:

```bash
cd backend-api
yarn install
```

### Veritabanını Hazırlayın

Önce MongoDB'yi başlatın:

```bash
# Yerel MongoDB örneği için
mongod --dbpath /path/to/your/data/directory
```

Ardından test verilerini yükleyin:

```bash
# Monorepo kök dizininde
yarn workspace onlyvips-backend-api seed

# Veya doğrudan backend-api dizininde
yarn seed
```

### Uygulamayı Başlatın

Monorepo üzerinden:

```bash
# Kök dizinde
yarn start:backend
```

Doğrudan backend-api dizininde:

```bash
# Geliştirme modunda
yarn dev

# Üretim modunda
yarn build
yarn start
```

## 📡 API Kullanımı

### Kimlik Doğrulama

API'nin çoğu endpoint'i kimlik doğrulama gerektirir. İlk olarak, bir token almanız gerekir:

#### Telegram ile Giriş

```bash
curl -X POST http://localhost:8000/api/auth/telegram \
  -H "Content-Type: application/json" \
  -d '{
    "telegramId": "123456789",
    "username": "user123",
    "firstName": "Test",
    "lastName": "User",
    "photoUrl": "https://example.com/photo.jpg"
  }'
```

Yanıt:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "telegramId": "123456789",
    "username": "user123",
    "firstName": "Test",
    "lastName": "User",
    "profilePhoto": "https://example.com/photo.jpg",
    "isShowcu": false,
    "xp": 0,
    "badges": [],
    "stars": 0
  }
}
```

#### Token Kullanımı

Alınan token'ı tüm korumalı API çağrılarında kullanın:

```bash
curl -X GET http://localhost:8000/api/profile \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### İçerik Yönetimi

#### İçerik Listeleme

```bash
curl -X GET "http://localhost:8000/api/content?page=1&limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

#### İçerik Oluşturma (Şovcular için)

```bash
curl -X POST http://localhost:8000/api/content \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "title": "Test İçerik",
    "description": "Bu bir test içeriktir",
    "mediaUrl": "https://example.com/media.jpg",
    "mediaType": "image",
    "contentCategory": "örnek",
    "tags": ["test", "örnek"],
    "isPremium": true,
    "price": 10
  }'
```

### VIP Paket Yönetimi

#### Paket Oluşturma (Şovcular için)

```bash
curl -X POST http://localhost:8000/api/packages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "name": "Premium Paket",
    "description": "Tüm içeriklere erişim",
    "price": 50,
    "duration": 30,
    "features": ["Özel içerikler", "Öncelikli erişim"]
  }'
```

#### Pakete Abone Olma

```bash
curl -X POST http://localhost:8000/api/packages/PACKAGE_ID/subscribe \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "transactionHash": "your_ton_transaction_hash"
  }'
```

### Görev Sistemi

#### Görevleri Listeleme

```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

#### Görev Tamamlama

```bash
curl -X POST http://localhost:8000/api/tasks/complete \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "taskId": 1,
    "verificationData": {
      "additionalInfo": "Doğrulama için ek bilgi"
    }
  }'
```

## 🐳 Docker ile Çalıştırma

Docker ve Docker Compose kullanarak tüm sistemi tek komutla başlatabilirsiniz:

```bash
# Projenin kök dizininde
cd docker-config
docker-compose up -d
```

Bu komut, tüm servisleri (MongoDB, backend API, flirt-bot, miniapp, showcu-panel) başlatacaktır.

## 🔄 Common-Modules ile Entegrasyon

Backend API'ye yeni tipler veya yardımcı fonksiyonlar eklerken, `common-modules` paketindeki ortak bileşenleri kullanmayı unutmayın:

```typescript
// src/models/user.ts
import { User } from 'onlyvips-common';
import { Document } from 'mongoose';

// MongoDB şemasını ortak tiplerle genişletme
export interface IUserDocument extends User, Document {
  // MongoDB spesifik alanlar
  createdAt: Date;
  updatedAt: Date;
}
```

## 🔍 Hata Ayıklama

### Logları İzleme

```bash
# Geliştirme ortamında
yarn dev

# Docker ortamında
docker logs -f onlyvips-backend
```

### Veritabanı Kontrolleri

MongoDB Shell kullanarak veritabanını inceleyebilirsiniz:

```bash
mongosh
use onlyvips
db.users.find()  # Kullanıcı verilerini görüntüle
db.contents.find()  # İçerik verilerini görüntüle
```

## 📚 Daha Fazla Belge

- [API Dokümantasyonu](API_DOCS.md)
- [Veritabanı Şeması](DB_SCHEMA.md)
- [Değişiklik Günlüğü](CHANGES.md)
- [Monorepo Ana Sayfası](../../README.md)

---

© 2024 SiyahKare. Tüm hakları saklıdır. 