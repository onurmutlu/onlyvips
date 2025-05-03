# OnlyVips Flirt-Bot

OnlyVips ekosisteminin Telegram bot bileşenidir. Görev doğrulama, kullanıcı etkileşimi ve yapay zeka asistanı olarak hizmet eder.

## 🚀 Özellikler

- **Görev Doğrulama**: 8+ farklı görev tipini otomatik doğrular
- **GPT Entegrasyonu**: Yapay zeka destekli flört koçluğu sağlar
- **XP ve Rozet Sistemi**: Kullanıcı ilerlemesini takip eder
- **Webhook Desteği**: MiniApp ve Backend API ile entegrasyon
- **TON Ödeme Entegrasyonu**: Blockchain ödeme takibi

## 🛠️ Teknolojiler

- **Python 3.9+**: Ana programlama dili
- **Telethon**: Telegram client kütüphanesi
- **OpenAI API**: GPT entegrasyonu
- **Redis**: Geçici veri saklama
- **Async I/O**: Yüksek performanslı asenkron işlemler

## 📋 Monorepo'da Kullanım

Bu bot, monorepo yapısında Poetry ile yönetilmektedir. Root dizinden şu şekilde çalıştırabilirsiniz:

```bash
# Bot'u başlatmak için
yarn start:bot

# Veya doğrudan
cd flirt-bot
poetry run bot
```

## 🚀 Kurulum

### Gereksinimler

- Python 3.9+
- Poetry
- Telegram API anahtarları (API ID ve Hash)
- OpenAI API anahtarı
- Redis (isteğe bağlı)

### Monorepo Üzerinden Kurulum

1. Bağımlılıkları yükleyin:
   ```bash
   # Root dizinde
   yarn install
   poetry install
   ```

2. `.env` dosyasını oluşturun:
   ```bash
   cd flirt-bot
   cp .env.example .env
   ```

3. `.env` dosyasını düzenleyin:
   ```
   TELEGRAM_API_ID=your_api_id
   TELEGRAM_API_HASH=your_api_hash
   TELEGRAM_BOT_TOKEN=your_bot_token
   OPENAI_API_KEY=your_openai_key
   BACKEND_API_URL=http://localhost:8000
   ```

4. (İsteğe bağlı) Telethon oturumu oluşturun:
   ```bash
   cd flirt-bot
   poetry run python session_generator.py
   ```

5. Bot'u başlatın:
   ```bash
   # Root dizinde
   yarn start:bot
   
   # Veya flirt-bot dizininde
   poetry run bot
   ```

## 📦 Proje Yapısı

```
flirt-bot/
├── src/
│   ├── api/              # Backend API istekleri
│   ├── core/             # Ana bot işlevleri
│   ├── tasks/            # Görev işleyicileri
│   │   ├── plugins/      # Görev eklentileri
│   │   └── task_types/   # Görev tipleri
│   └── utils/            # Yardımcı fonksiyonlar
├── bot_listener.py       # Ana bot betiği
├── pyproject.toml        # Poetry yapılandırması
└── session_generator.py  # Oturum oluşturucu
```

## 🔄 Görev Tipleri

Bot, aşağıdaki görev tiplerini destekler:

- `bot_mention`: Kullanıcının botu bir grupta etiketlemesi
- `channel_join`: Belirtilen kanala katılma
- `group_join`: Belirtilen gruba katılma
- `forward_message`: Belirli bir mesajı yönlendirme
- `post_share`: İçeriği paylaşma
- `deeplink_track`: Özel link takibi
- `pin_check`: Mesaj sabitleme kontrolü
- `message`: Belirli bir mesajı gönderme
- `referral`: Yeni kullanıcı davet etme
- `invite_tracker`: Gruba davet etme
- `share_count`: Paylaşım sayısı takibi

## 🤖 Komutlar

Bot aşağıdaki komutları destekler:

- `/start`: Bot'u başlatır ve karşılama mesajı gönderir
- `/miniapp`: MiniApp'i açar
- `/help`: Yardım mesajı gösterir
- `/profile`: Kullanıcı profilini gösterir
- `/tasks`: Görevleri listeler
- `/flirt`: Flört koçu modunu başlatır
- `/wallet`: Cüzdan bilgilerini gösterir

## 🔄 Monorepo Entegrasyonu

Bu bot, monorepo yapısındaki diğer bileşenlerle aşağıdaki şekilde entegre olur:

1. **Backend API**: Bot, görev doğrulama sonuçlarını API'ye bildirir
   ```python
   from src.api.tasks import verify_task
   
   # Görev doğrulama örneği
   await verify_task(user_id, task_id, verification_data)
   ```

2. **Poetry Yapılandırması**: Bağımlılıklar root pyproject.toml'dan yönetilir

3. **Ortak Yapılandırma**: Ortam değişkenleri ve yapılandırma mantığı paylaşılır

## 🧪 Test

```bash
# flirt-bot dizininde
poetry run pytest
```

## 🔧 Hata Ayıklama

Bot'u debug modunda başlatmak için:

```bash
# Verbose loglarla başlatma
poetry run python bot_listener.py --verbose
```

## 📄 Lisans

© 2024 SiyahKare. Tüm hakları saklıdır.
