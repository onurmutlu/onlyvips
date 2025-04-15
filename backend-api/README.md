
# OnlyVips Backend API

OnlyVips projesinin backend API hizmetleri.

## Özellikler

- İçerik yönetimi API'leri
- Şovcu panel entegrasyonu
- Kullanıcı ve abonelik yönetimi
- TON ödeme sistemi entegrasyonu
- Güvenli kimlik doğrulama

## Kurulum

1. Gereklilikleri yükleyin:
```bash
npm install
```

2. `.env` dosyasını oluşturun:
```bash
cp .env.example .env
```

3. `.env` dosyasını düzenleyin ve gerekli değerleri girin:
```
PORT=3000
MONGODB_URI=mongodb://localhost:27017/onlyvips
JWT_SECRET=your_jwt_secret
TON_WALLET_ADDRESS=your_ton_wallet_address
```

## Çalıştırma

Geliştirme ortamında çalıştırmak için:
```bash
npm run dev
```

Üretim ortamında çalıştırmak için:
```bash
npm run build
npm start
```

## Docker ile Çalıştırma

```bash
docker build -t onlyvips-api .
docker run -p 5000:5000 -v ./uploads:/app/uploads onlyvips-api
```

## API Rotaları

- `/content` - İçerik yönetimi
- `/creators` - Şovcu profil yönetimi
- `/users` - Kullanıcı işlemleri
- `/packages` - Paket ve abonelik yönetimi
- `/payments` - Ödeme işlemleri
- `/creator-panel` - Şovcu panel API'leri

## API Belgeleri

API çalıştıktan sonra `/docs` adresinden Swagger UI ile API belgelerine erişebilirsiniz.

## Maliyet Optimizasyonu

OpenAI API maliyetlerini azaltmak için:

1. `OPENAI_MODEL` için daha ucuz model kullanılmaktadır (gpt-3.5-turbo-instruct)
2. `GPT_MAX_USAGE_DAY` ile kullanıcı başına günlük kullanım sınırlandırılmıştır
3. `GPT_MAX_TOKENS` ile yanıt başına token sayısı sınırlandırılmıştır

## Proje Yapısı

```
backend-api/
├── app/
│   ├── controllers/    # API endpoint işleyicileri
│   ├── middleware/     # Kimlik doğrulama, hata işleme
│   ├── models/         # Veritabanı modelleri
│   ├── routes/         # API rotaları
│   ├── services/       # İş mantığı servisleri
│   └── utils/          # Yardımcı fonksiyonlar
├── main.py             # Uygulama giriş noktası
├── requirements.txt    # Proje bağımlılıkları
├── Dockerfile          # Docker yapılandırması
└── README.md           # Bu dosya
```

## Deployment Kontrol Listesi

- [ ] Veritabanı bağlantısı kontrol edildi
- [ ] .env dosyası yapılandırıldı
- [ ] API rotaları test edildi
- [ ] TON ödeme sistemi test edildi
- [ ] Rate limiting yapılandırıldı
- [ ] HTTPS yapılandırması tamamlandı

