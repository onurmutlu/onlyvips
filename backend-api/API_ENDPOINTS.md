# OnlyVips API Endpoints Documentation

## Genel Bakış
OnlyVips Backend API, FastAPI framework'ü kullanılarak geliştirilmiş, production-ready bir REST API'dir.

**Toplam Endpoint Sayısı:** 64  
**API Version:** v1  
**Base URL:** `http://localhost:8000/api`

---

## 🔐 Authentication (`/api/auth`)

Kullanıcı kimlik doğrulama ve yetkilendirme işlemleri.

### Endpoints
- `POST /auth/register` - Yeni kullanıcı kaydı
- `POST /auth/login` - Kullanıcı girişi (JWT token)
- `POST /auth/telegram` - Telegram üzerinden giriş
- `POST /auth/refresh` - Token yenileme
- `GET /auth/me` - Mevcut kullanıcı bilgileri
- `POST /auth/logout` - Çıkış yapma

### Özellikler
- JWT token authentication
- Telegram hash validation
- Token rotation (saatlik)
- Token blacklist sistemi
- Rate limiting (5 req/min)

---

## 👥 Users (`/api/users`)

Kullanıcı profil yönetimi ve takip işlemleri.

### Endpoints
- `GET /users/me` - Kendi profil bilgilerim
- `PUT /users/me` - Profil güncelleme
- `GET /users/{user_id}` - Kullanıcı profil detayı
- `POST /users/{user_id}/follow` - Kullanıcıyı takip et
- `DELETE /users/{user_id}/follow` - Takibi bırak
- `GET /users/{user_id}/followers` - Takipçi listesi
- `GET /users/{user_id}/following` - Takip edilenler listesi
- `GET /users/search` - Kullanıcı arama

### Özellikler
- Profil cache (TTL: 10 dakika)
- Takip sistemi
- Avatar/cover yönetimi
- Bio ve sosyal linkler

---

## 📋 Tasks (`/api/tasks`)

Görev tabanlı kullanıcı etkileşim sistemi.

### Endpoints
- `GET /tasks` - Aktif görev listesi
- `GET /tasks/{task_id}` - Görev detayı
- `POST /tasks/{task_id}/start` - Görevi başlat
- `POST /tasks/{task_id}/complete` - Görevi tamamla
- `GET /tasks/user/{user_id}` - Kullanıcının görevleri
- `GET /tasks/leaderboard` - Lider tablosu
- `POST /tasks/create` - Yeni görev oluştur (admin)
- `PUT /tasks/{task_id}` - Görev güncelle (admin)
- `DELETE /tasks/{task_id}` - Görev sil (admin)

### Görev Tipleri
- `telegram_join` - Telegram kanalına katılma
- `telegram_message` - Mesaj gönderme
- `content_view` - İçerik görüntüleme
- `content_like` - İçerik beğenme
- `referral` - Referans getirme
- `daily_login` - Günlük giriş
- `survey` - Anket doldurma

### Özellikler
- Otomatik doğrulama sistemi
- Ödül dağıtımı (coin/XP/rozet)
- Görev cache (TTL: 5 dakika)
- Streak tracking
- Anti-cheat mekanizması

---

## 🏆 Badges (`/api/badges`)

Rozet (achievement) yönetim sistemi.

### Endpoints
- `GET /badges` - Tüm rozetler
- `GET /badges/{badge_id}` - Rozet detayı
- `GET /badges/user/{user_id}` - Kullanıcının rozetleri
- `POST /badges/{badge_id}/claim` - Rozet talep et
- `POST /badges/create` - Rozet oluştur (admin)
- `PUT /badges/{badge_id}` - Rozet güncelle (admin)
- `DELETE /badges/{badge_id}` - Rozet sil (admin)

### Rozet Kategorileri
- `achievement` - Başarım rozetleri
- `special` - Özel rozetler
- `seasonal` - Sezonluk rozetler
- `rank` - Seviye rozetleri

### Özellikler
- Otomatik rozet kazanma
- Rozet rarity sistemi (common, rare, epic, legendary)
- Progress tracking
- Rozet showcase

---

## 📁 Content (`/api/content`)

İçerik yönetimi ve medya işlemleri.

### Endpoints
- `GET /content` - İçerik listesi (filtreleme, sayfalama)
- `GET /content/{content_id}` - İçerik detayı
- `POST /content/upload` - Yeni içerik yükleme
- `PUT /content/{content_id}` - İçerik güncelleme
- `DELETE /content/{content_id}` - İçerik silme
- `POST /content/{content_id}/like` - İçerik beğenme
- `POST /content/{content_id}/view` - Görüntüleme sayısını artır

### Desteklenen Medya Tipleri
- **Görsel:** `.jpg`, `.jpeg`, `.png`, `.gif`
- **Video:** `.mp4`, `.mov`
- **Ses:** `.mp3`, `.wav`
- **Doküman:** `.pdf`, `.doc`, `.docx`

### Özellikler
- File upload (max 50MB)
- File hash validation
- Automatic thumbnail generation
- Premium/freemium content
- Content categorization
- View/like analytics
- Cache layer (TTL: 10 dakika)

---

## 🎭 Showcus (`/api/showcus`)

İçerik üretici (creator) yönetimi ve analitik.

### Endpoints
- `GET /showcus` - Üretici listesi
- `GET /showcus/{showcu_id}` - Üretici profil detayı
- `GET /showcus/{showcu_id}/stats` - İstatistikler (cache'li)
- `GET /showcus/{showcu_id}/earnings` - Kazanç bilgileri
- `PUT /showcus/{showcu_id}` - Profil güncelleme
- `POST /showcus/{showcu_id}/verify` - Doğrulama (admin)
- `POST /showcus/{showcu_id}/subscription` - Abonelik planı oluşturma
- `GET /showcus/{showcu_id}/contents` - Üreticinin içerikleri
- `POST /showcus/{showcu_id}/payout` - Ödeme talebi

### Üretici Seviyeleri
- **Basic:** Ücretsiz başlangıç seviyesi
- **Pro:** Aylık $9.99, gelişmiş özellikler
- **Premium:** Aylık $29.99, tüm özellikler

### Özellikler
- Creator verification
- Earnings dashboard
- Content analytics
- Subscriber management
- Payout system (min: $50)
- Commission tracking (%15)

---

## 💰 Payments (`/api/payments`)

Ödeme ve TON cüzdan entegrasyonu.

### Endpoints
- `GET /payments/wallet` - Cüzdan bilgileri
- `POST /payments/wallet/connect` - TON cüzdan bağlama
- `POST /payments/purchase/content` - İçerik satın alma
- `POST /payments/subscribe` - Abonelik ödemesi
- `POST /payments/tip` - Bahşiş gönderme
- `POST /payments/withdraw` - Para çekme
- `GET /payments/transactions` - İşlem geçmişi
- `GET /payments/payment/{payment_id}` - Ödeme detayları
- `GET /payments/balance` - Bakiye özeti

### Ödeme Tipleri
- **Content Purchase:** İçerik satın alma (5% komisyon)
- **Subscription:** Aylık abonelik (3% komisyon)
- **Tip:** Bahşiş (2% komisyon)
- **Withdrawal:** Para çekme (1% komisyon)

### Özellikler
- TON blockchain entegrasyonu
- Multi-currency support (TON, USD, TRY)
- Transaction history
- Automatic commission calculation
- Minimum withdrawal: 1 TON
- Minimum tip: 0.1 TON

---

## 🛡️ Admin (`/api/admin`)

Sistem yönetimi ve moderasyon.

### Endpoints
- `GET /admin/stats` - Admin dashboard istatistikleri
- `GET /admin/users` - Kullanıcı yönetimi
- `GET /admin/content/moderation` - İçerik moderasyon kuyruğu
- `POST /admin/content/{content_id}/moderate` - İçerik moderasyonu
- `POST /admin/users/{user_id}/ban` - Kullanıcı banlama
- `POST /admin/users/{user_id}/unban` - Ban kaldırma
- `GET /admin/settings` - Sistem ayarları
- `PUT /admin/settings` - Sistem ayarları güncelleme
- `GET /admin/reports` - Şikayet raporları
- `GET /admin/analytics/revenue` - Gelir analitiği

### Moderasyon Aksiyonları
- `approve` - İçeriği onayla
- `reject` - İçeriği reddet
- `delete_content` - İçeriği sil
- `ban_user` - Kullanıcıyı banla (1-365 gün)

### Özellikler
- Role-based access control
- Content moderation queue
- User ban system (temporary/permanent)
- System settings management
- Revenue analytics
- Report management

---

## 🏥 Health (`/api/health`)

Sistem sağlık durumu ve monitoring.

### Endpoints
- `GET /health` - Basit sağlık kontrolü
- `GET /health/detailed` - Detaylı sağlık raporu
- `GET /health/readiness` - Kubernetes readiness probe
- `GET /health/liveness` - Kubernetes liveness probe
- `GET /health/metrics` - Prometheus metrics

### Kontrol Edilen Servisler
- Database (MongoDB)
- Redis cache
- External APIs (Telegram, OpenAI)
- Disk space
- Memory usage

---

## 🔒 Güvenlik Özellikleri

### Rate Limiting
- IP-based ve user-based limiting
- Sliding window algoritması
- Endpoint-specific limits
- Redis-backed

### Input Validation
- SQL injection protection
- XSS filtering
- Path traversal protection
- Command injection prevention
- HTML sanitization (bleach)

### JWT Security
- Token rotation (saatlik)
- Token blacklist
- Telegram hash validation
- Automatic token refresh

### Middleware Stack
1. **MetricsMiddleware** - Prometheus metrics
2. **RateLimitingMiddleware** - Rate limiting
3. **InputValidationMiddleware** - Input sanitization
4. **JWTSecurityMiddleware** - Token validation

---

## 📊 Monitoring & Logging

### Prometheus Metrics
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request duration
- `http_requests_active` - Active requests
- `http_request_size_bytes` - Request size
- `http_response_size_bytes` - Response size

### Structured Logging
- Request/response logging
- Error tracking (Sentry)
- Performance monitoring
- Audit logs

---

## 🚀 Cache Strategy

### Cache Layers
- **User Cache:** 10 dakika TTL
- **Content Cache:** 10 dakika TTL
- **Task Cache:** 5 dakika TTL
- **Stats Cache:** 5 dakika TTL

### Cache Invalidation
- Pattern-based invalidation
- Manual invalidation endpoints
- Automatic cache refresh

---

## 📝 API Kullanım Örnekleri

### Authentication
```bash
# Kullanıcı kaydı
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "telegram_id": "123456789"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=johndoe&password=SecurePass123!"
```

### Content Upload
```bash
curl -X POST http://localhost:8000/api/content/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@image.jpg" \
  -F "title=My Amazing Photo" \
  -F "category=photography" \
  -F "is_premium=false"
```

### Payment
```bash
# İçerik satın alma
curl -X POST http://localhost:8000/api/payments/purchase/content \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 5.0,
    "currency": "TON",
    "description": "Premium content purchase",
    "recipient_id": "creator_123"
  }'
```

---

## 🐳 Docker Deployment

```bash
# Build
docker build -t onlyvips-api .

# Run
docker run -p 8000:8000 \
  -e MONGODB_URI=mongodb://localhost:27017 \
  -e REDIS_HOST=localhost \
  -e JWT_SECRET=your-secret-key \
  onlyvips-api
```

---

## 📚 API Documentation

### Swagger UI
Canlı API dokümantasyonu: `http://localhost:8000/docs`

### ReDoc
Alternatif dokümantasyon: `http://localhost:8000/redoc`

### OpenAPI Schema
JSON schema: `http://localhost:8000/openapi.json`

---

## 🔧 Development

### Gereksinimler
- Python 3.11+
- MongoDB 6.0+
- Redis 7.0+
- Node.js 18+ (Frontend için)

### Kurulum
```bash
cd backend-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Test
```bash
# Tüm testler
pytest

# Coverage raporu
pytest --cov=app --cov-report=html

# Sadece birim testleri
pytest tests/unit/

# Sadece entegrasyon testleri
pytest tests/integration/
```

---

## 📞 Destek

**GitHub:** https://github.com/yourusername/OnlyVips  
**Email:** support@onlyvips.com  
**Telegram:** @OnlyVipsSupport

---

**Son Güncelleme:** 3 Ekim 2025  
**API Versiyonu:** 1.0.0  
**Durum:** Production Ready ✅

