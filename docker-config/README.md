# Docker Yapılandırması

Bu dizin, OnlyVips platformunun tüm servislerini Docker ortamında çalıştırmak için gerekli konfigürasyon dosyalarını içerir.

## 📋 İçerik

- `docker-compose.yml`: Tüm servisleri tek bir komutla başlatmanızı sağlayan kompozisyon dosyası
- `nginx.conf`: (isteğe bağlı) Tercihen Nginx proxy yapılandırması

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler

- Docker
- Docker Compose

### Ortam Hazırlığı

1. Projenin kök dizininde `.env` dosyasını oluşturun:
   ```bash
   cd ..
   cp .env.example .env
   ```

2. `.env` dosyasını düzenleyin ve gerekli ortam değişkenlerini ayarlayın.

### Servisleri Başlatmak

```bash
cd docker-config
docker-compose up -d
```

Bu komut aşağıdaki servisleri başlatacaktır:
- MongoDB (veritabanı)
- Backend API (Express/TypeScript API)
- Şovcu Panel (React kontrol paneli)
- MiniApp (React kullanıcı arayüzü)
- Flirt-Bot (Python Telegram bot)

### Servisleri Durdurma

```bash
docker-compose down
```

Veritabanını da silmek için:
```bash
docker-compose down -v
```

## 🔄 Servis Özelleştirmeleri

Her servis için özel yapılandırmalar `docker-compose.yml` dosyasında düzenlenebilir:

### MongoDB

```yaml
mongodb:
  environment:
    - MONGO_INITDB_ROOT_USERNAME=root
    - MONGO_INITDB_ROOT_PASSWORD=changeme  # Bu değeri değiştirin
```

### Backend API

```yaml
backend:
  environment:
    - JWT_SECRET=your_secure_jwt_secret  # Bu değeri değiştirin
    - CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### Flirt-Bot

Telegram bot token'ınızı ayarlamayı unutmayın:

```yaml
flirtbot:
  environment:
    - TELEGRAM_BOT_TOKEN=your_bot_token  # @BotFather ile aldığınız token
```

## 📊 Ortam Kontrol Listesi

- [ ] MongoDB kullanıcı adı ve şifresi değiştirildi
- [ ] JWT_SECRET güvenli bir değerle değiştirildi
- [ ] TELEGRAM_BOT_TOKEN ayarlandı
- [ ] CORS_ORIGINS üretim ortamı için uygun şekilde yapılandırıldı
- [ ] Dosya paylaşımları için volume'lar yapılandırıldı

## 📄 Lisans

© 2024 SiyahKare. Tüm hakları saklıdır.