# OnlyVips - Telegram Görev ve Rozet Platformu | v0.8.0

OnlyVips, Telegram kullanıcılarının çeşitli görevleri tamamlayarak deneyim puanı (XP) kazanabilecekleri ve özel rozetler elde edebilecekleri bir sosyal etkileşim platformudur. Platform, Telegram ekosistemine entegre olarak, kullanıcı katılımını artırmak ve topluluk etkileşimini güçlendirmek için tasarlanmıştır.

## Ana Bileşenler

Proje, aşağıdaki ana bileşenlerden oluşmaktadır:

1. **Backend API (backend-api)**: FastAPI tabanlı REST API servisi, MongoDB entegrasyonu ve JWT kimlik doğrulama
2. **Flirt-Bot (flirt-bot)**: Telegram bot bileşeni, görev doğrulama ve yapay zeka desteği
3. **MiniApp (miniapp)**: Telegram Mini Uygulama, TON cüzdan entegrasyonu
4. **Showcu Panel (showcu-panel)**: Yönetici kontrol paneli, içerik ve VIP paket yönetimi

## 🚀 Başlangıç 

### Gereksinimler

- Python 3.9+
- Node.js 18+
- MongoDB 5.0+ (veya development için bellek veritabanı)
- Telegram Bot API anahtarı
- OpenAI API anahtarı (GPT özelliği için)

### Kurulum

1. Projeyi klonlayın:
   ```
   git clone https://github.com/yourusername/OnlyVips.git
   cd OnlyVips
   ```

2. Kurulum scriptini çalıştırın:
   ```
   ./install.sh
   ```

3. Çevre değişkenlerini ayarlayın:
   ```
   cp .env.example .env
   # .env dosyasını düzenleyin ve gereken bilgileri doldurun
   ```

4. Backend API servisini başlatın:
   ```
   cd backend-api
   python main.py
   ```

5. Telegram bot'unu başlatın:
   ```
   cd flirt-bot
   python bot_listener.py
   ```

6. MiniApp ve Admin panel'i geliştirme modunda başlatın:
   ```
   cd miniapp
   npm run dev
   
   cd ../showcu-panel
   npm run dev
   ```

## 🏗️ Proje Yapısı

```
OnlyVips/
├── backend-api/          # FastAPI tabanlı REST API
├── flirt-bot/            # Telegram bot bileşeni
├── miniapp/              # Telegram Mini Uygulama
├── showcu-panel/         # Admin kontrol paneli
├── common-modules/       # Tüm bileşenler için ortak modüller
├── charts/               # Helm chart'ları
├── docker-config/        # Docker yapılandırma dosyaları
├── scripts/              # Genel amaçlı scriptler
└── tests/                # Entegrasyon ve E2E testleri
```

## 🌟 Özellikler

### Kullanıcı Özellikler
- Telegram hesabı ile kimlik doğrulama
- Görev tamamlama ve XP kazanma
- Rozet elde etme
- Görev ilerlemesi takibi
- Seviye yükseltme
- TON cüzdan entegrasyonu

### Yönetici Özellikleri
- Görev oluşturma ve düzenleme
- Rozet yönetimi
- Kullanıcı yönetimi
- İçerik oluşturma ve VIP paket yapılandırma
- Metrik ve istatistik takibi
- Manuel görev doğrulama
- Gelir takibi ve ödeme yönetimi

## 🛠️ Geliştirme

### Backend API
FastAPI tabanlı REST API servisi, MongoDB veritabanı ve JWT kimlik doğrulama sistemiyle çalışır. Görev yönetimi, kullanıcı yönetimi ve rozet sistemini içerir.

```
cd backend-api
pip install -r requirements.txt
python main.py
```

API dokümantasyonu: http://localhost:8000/api/docs

### Flirt-Bot
Telegram bot bileşeni, kullanıcıların görevlerle etkileşime girmesini, görevleri tamamlamasını ve OpenAI entegrasyonu ile flört tavsiyeleri almasını sağlar.

```
cd flirt-bot
pip install -r requirements.txt
python bot_listener.py
```

### MiniApp
Telegram Mini Uygulama, kullanıcıların görevleri ve ilerlemelerini görüntülemek için kullanılır. TON blockchain ile entegre çalışır.

```
cd miniapp
npm install
npm run dev
```

### Showcu Panel
Yönetici kontrol paneli, görevleri, kullanıcıları, içerikleri ve VIP paketleri yönetmek için kullanılır.

```
cd showcu-panel
npm install
npm run dev
```

## 📦 Dağıtım

Proje, Docker ve Kubernetes üzerinde dağıtım için yapılandırılmıştır. Detaylı dağıtım bilgileri için `README-PROD-ROLLOUT.md` dosyasına bakın.

## 📄 Lisans

Bu proje OnlyVips ekibi tarafından geliştirilmiştir. Tüm hakları saklıdır.
