# OnlyVips - Telegram Görev ve Rozet Platformu | v0.9.0

OnlyVips, Telegram kullanıcılarının çeşitli görevleri tamamlayarak deneyim puanı (XP) kazanabilecekleri, özel rozetler elde edebilecekleri ve premium içeriklere erişebilecekleri bir sosyal etkileşim platformudur. Platform, Telegram ekosistemine entegre olarak, kullanıcı katılımını artırmak ve topluluk etkileşimini güçlendirmek için tasarlanmıştır.

## 🚀 Özellikler

### Kullanıcı Özellikleri
- ✅ Telegram hesabı ile güvenli kimlik doğrulama
- ✅ Görev tamamlama ve XP/Token kazanma sistemi
- ✅ Seviye atlama ve rozet koleksiyonu
- ✅ Premium içeriklere görev tabanlı erişim
- ✅ TON cüzdan entegrasyonu ve ödeme sistemi
- ✅ Gerçek zamanlı bildirimler
- ✅ Çoklu dil desteği (TR/EN)

### İçerik Üretici (Showcu) Özellikleri
- ✅ Gelişmiş içerik yönetim paneli
- ✅ Görev oluşturma ve yönetimi
- ✅ VIP paket ve abonelik sistemi
- ✅ Detaylı analitik ve gelir takibi
- ✅ TON ile otomatik ödeme sistemi
- ✅ İçerik moderasyon araçları

### Teknik Özellikler
- ✅ Mikroservis mimarisi hazırlığı
- ✅ Redis cache katmanı
- ✅ Prometheus/Grafana monitoring
- ✅ Canary deployment desteği
- ✅ Otomatik yedekleme sistemi
- ✅ Rate limiting ve DDoS koruması
- ✅ Sentry error tracking

## 📋 Ana Bileşenler

Proje, aşağıdaki ana bileşenlerden oluşmaktadır:

1. **Backend API (backend-api)**: FastAPI tabanlı REST API servisi, MongoDB entegrasyonu, JWT kimlik doğrulama ve Redis cache
2. **Flirt-Bot (flirt-bot)**: Telegram bot bileşeni, görev doğrulama, yapay zeka desteği ve bildirim sistemi
3. **MiniApp (miniapp)**: Telegram Mini Uygulama, React/TypeScript, TON cüzdan entegrasyonu, PWA desteği
4. **Showcu Panel (showcu-panel)**: İçerik üretici kontrol paneli, gelişmiş analitik, ödeme yönetimi
5. **Monitoring Stack**: Prometheus, Grafana, Loki, AlertManager ile tam monitoring çözümü

## 🛠️ Teknoloji Stack

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: MongoDB (Primary), Redis (Cache)
- **Authentication**: JWT + OAuth2 + Token Rotation
- **Task Queue**: Celery + Redis
- **API Documentation**: OpenAPI/Swagger
- **Security**: Rate Limiting, Input Validation, JWT Security
- **Monitoring**: Sentry Error Tracking, Prometheus Metrics
- **Caching**: Redis-based multi-layer caching

### Frontend
- **Framework**: React 18 + TypeScript
- **State Management**: Zustand
- **Styling**: TailwindCSS
- **Build Tool**: Vite
- **UI Components**: Ant Design

### DevOps
- **Container**: Docker (Multi-stage builds)
- **Orchestration**: Kubernetes + Helm
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Logging**: Loki + Promtail

## 🚀 Hızlı Başlangıç

### Gereksinimler

- Python 3.11+
- Node.js 18+ ve npm 9+
- MongoDB 6.0+
- Redis 7.0+
- Docker & Docker Compose
- Telegram Bot API anahtarı
- OpenAI API anahtarı (opsiyonel)
- TON wallet (ödeme sistemi için)

### Kurulum

1. **Projeyi klonlayın**:
   ```bash
   git clone https://github.com/yourusername/OnlyVips.git
   cd OnlyVips
   ```

2. **Otomatik kurulum**:
   ```bash
   ./install.sh
   ```

3. **Çevre değişkenlerini ayarlayın**:
   ```bash
   cp .env.example .env
   # .env dosyasını düzenleyin ve gereken bilgileri doldurun
   ```

4. **Docker ile başlatın**:
   ```bash
   docker-compose up -d
   ```

### Manuel Kurulum

<details>
<summary>Detaylı manuel kurulum adımları</summary>

1. **Backend API**:
   ```bash
   cd backend-api
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. **Telegram Bot**:
   ```bash
   cd flirt-bot
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python bot_listener.py
   ```

3. **MiniApp**:
   ```bash
   cd miniapp
   npm install
   npm run dev
   ```

4. **Showcu Panel**:
   ```bash
   cd showcu-panel
   npm install
   npm run dev
   ```
</details>

## 🏗️ Proje Yapısı

```
OnlyVips/
├── backend-api/          # FastAPI REST API servisi
│   ├── app/             # Ana uygulama kodu
│   ├── tests/           # Unit ve integration testler
│   └── Dockerfile       # Production-ready Dockerfile
├── flirt-bot/           # Telegram bot bileşeni
│   ├── src/             # Bot kaynak kodları
│   └── plugins/         # Görev eklentileri
├── miniapp/             # Telegram Mini Uygulama
│   ├── src/             # React uygulama kodu
│   └── public/          # Statik dosyalar
├── showcu-panel/        # İçerik üretici paneli
│   ├── src/             # React uygulama kodu
│   └── public/          # Statik dosyalar
├── common-modules/      # Paylaşılan modüller
├── charts/              # Kubernetes Helm charts
├── docker-config/       # Docker yapılandırmaları
│   └── monitoring/      # Monitoring stack
├── scripts/             # Deployment ve utility scriptler
│   ├── production-deploy.sh
│   ├── canary-deploy.sh
│   └── rollback.sh
└── tests/               # E2E testler
```

## 🚀 Production Deployment

### Hızlı Production Deployment

```bash
# Tek komutla production deployment
./scripts/production-deploy.sh
```

### Deployment Özellikleri

- ✅ **Canary Deployment**: %10 trafik ile güvenli deployment
- ✅ **Otomatik Rollback**: Hata durumunda otomatik geri dönüş
- ✅ **Health Checks**: Tüm servisler için sağlık kontrolleri
- ✅ **Zero Downtime**: Kesintisiz deployment
- ✅ **Backup & Restore**: Otomatik yedekleme sistemi

### Monitoring

Production ortamında monitoring için:

```bash
# Monitoring stack'i başlat
cd docker-config/monitoring
docker-compose -f docker-compose.monitoring.yml up -d
```

Erişim adresleri:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3003 (admin/onlyvips123)
- AlertManager: http://localhost:9093

## 🔐 Güvenlik

- JWT tabanlı kimlik doğrulama
- Rate limiting ve DDoS koruması
- HTTPS/TLS zorunluluğu
- Input validation ve sanitization
- SQL injection koruması
- XSS ve CSRF koruması
- Güvenli secret yönetimi (HashiCorp Vault/AWS SSM)
- Regular security audits

## 📊 API Dokümantasyonu

Backend API dokümantasyonuna erişim:
- Development: http://localhost:8000/docs
- Production: https://api.onlyvips.com/docs

## 🧪 Test

```bash
# Backend testleri
cd backend-api
pytest --cov=app tests/

# Frontend testleri
cd miniapp
npm test

# E2E testleri
cd tests
npm run test:e2e
```

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

Bu proje OnlyVips ekibi tarafından geliştirilmiştir. Tüm hakları saklıdır.

## 📞 İletişim

- Website: [https://onlyvips.com](https://onlyvips.com)
- Email: support@onlyvips.com
- Telegram: [@OnlyVipsSupport](https://t.me/OnlyVipsSupport)

## 🔗 Faydalı Bağlantılar

- [Changelog](CHANGELOG.MD)
- [Roadmap](ROADMAP.MD)
- [Production Deployment Guide](README-PROD-ROLLOUT.md)
- [Security Policy](SECURITY.md)
- [API Documentation](https://api.onlyvips.com/docs)
