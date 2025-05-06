# OnlyVips Flirt-Bot | v0.8.0

OnlyVips ekosisteminin Telegram bot bileşenidir. Görev doğrulama, kullanıcı etkileşimi ve yapay zeka asistanı olarak hizmet eder.

## 🌟 Güncellemeler (v0.8.0)

Bu sürümde aşağıdaki önemli güncellemeler ve geliştirmeler yapılmıştır:

- **Backend API Entegrasyonu**: MongoDB veritabanı ile tam entegrasyon
- **Yapay Zeka İyileştirmeleri**: Daha doğal ve bağlam duyarlı yanıtlar
- **Görev Doğrulama Sistemi**: 18 farklı görev tipini destekleyen doğrulama mekanizması
- **Otomatik Test Sistemi**: Görev doğrulama için otomatik test senaryoları
- **Güvenlik İyileştirmeleri**: API key doğrulama ve güvenli bağlantı
- **Oturum Yönetimi**: Gelişmiş Telethon oturum yönetimi
- **Hata İşleme**: Kapsamlı hata ayıklama ve raporlama sistemi
- **Performans Optimizasyonu**: Asenkron işlem yönetimi ve bellek kullanımı iyileştirmeleri

## 🚀 Özellikler

- **Görev Doğrulama**: 10+ farklı görev tipini otomatik doğrular
- **Görev Yönetim Sistemi**: TaskManager ile farklı görev tiplerini kolay yönetme
- **GPT Entegrasyonu**: Yapay zeka destekli flört koçluğu sağlar
- **XP ve Rozet Sistemi**: Kullanıcı ilerlemesini takip eder
- **İlerleme İzleme**: Kullanıcıların görev ilerlemesini ve seviyelerini izler
- **MiniApp Entegrasyonu**: Telegram MiniApp ile entegre çalışır
- **Backend API Entegrasyonu**: Merkezi backend ile veri senkronizasyonu
- **Günlük Görev Sistemi**: Kullanıcılara günlük görevler sunar
- **Emoji Tepkisi Doğrulama**: Kullanıcıların emoji tepkilerini algılar
- **Grup Katılım ve Mesaj Kontrolü**: Grup katılımı ve sonraki mesajları doğrular

## 🛠️ Teknolojiler

- **Python 3.9+**: Ana programlama dili
- **Telethon**: Telegram client kütüphanesi
- **OpenAI API**: GPT entegrasyonu
- **Redis**: Geçici veri saklama
- **Async I/O**: Yüksek performanslı asenkron işlemler
- **FastAPI**: API endpoints için web framework
- **aiohttp**: Asenkron HTTP istekleri için
- **pydantic**: Veri doğrulama ve model tanımlama

## 🔌 API Entegrasyonu

Flirt-Bot, OnlyVips backend API'si ile tam entegre çalışır:

```python
# API ile görev tamamlamayı doğrulama
async def verify_task_completion(user_id: str, task_id: int, status: str = "approved"):
    """Görev tamamlama durumunu API'de doğrular"""
    try:
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": settings.BOT_API_KEY
        }
        
        # Doğrulama verilerini hazırla
        verification_data = {
            "user_id": user_id,
            "task_id": task_id,
            "status": status
        }
        
        # API isteği gönder
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{settings.BACKEND_API_URL}/api/tasks/verify",
                headers=headers,
                json=verification_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Görev doğrulama başarılı: {user_id}, {task_id}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Görev doğrulama hatası: {response.status}, {error_text}")
                    return None
    except Exception as e:
        logger.error(f"API isteği hatası: {str(e)}")
        return None
```

## 📋 Monorepo'da Kullanım

Bu bot, monorepo yapısında Poetry ile yönetilmektedir. Root dizinden şu şekilde çalıştırabilirsiniz:

```bash
# Bot'u başlatmak için
yarn start:bot

# Veya doğrudan
cd flirt-bot
poetry run python bot_listener.py
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
   BOT_API_KEY=your_bot_api_key
   BOT_USERNAME=your_bot_username
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
   poetry run python bot_listener.py
   ```

### Docker ile Çalıştırma

```bash
# Docker image oluşturma
docker build -t onlyvips-flirt-bot .

# Container başlatma
docker run -d --name flirt-bot --env-file .env onlyvips-flirt-bot
```

### BotFather Yapılandırması

Bot'u BotFather üzerinden yapılandırmak için aşağıdaki adımları izleyin:

1. Telegram'da [@BotFather](https://t.me/BotFather) ile sohbet başlatın
2. `/newbot` komutunu kullanarak yeni bir bot oluşturun (veya mevcut bir botu düzenleyin)
3. Bot'un adını ve kullanıcı adını belirleyin
4. Aldığınız BOT_TOKEN değerini `.env` dosyasına ekleyin
5. `/mybots` komutunu kullanarak botunuzu seçin
6. "Edit Bot" > "Edit Commands" seçeneğini kullanarak komutları tanımlayın:
   ```
   tasks - Mevcut görevleri gösterir
   myprogress - İlerleme durumunu gösterir
   gorev - Yeni bir görev al
   gorevlerim - Tüm görevlerini görüntüle
   gunluk - Günlük görev al
   flirt - Flört ipuçları al
   agent - Yapay zeka flört asistanı ile konuş
   flortcoach - Flört koçundan tavsiye al
   rozet - Sahip olduğun rozetleri görüntüle
   profil - Profil bilgilerini görüntüle
   miniapp - MiniApp'e erişim sağlar
   help - Yardım menüsünü gösterir
   ```
7. "Edit Bot" > "Inline Mode" > "Turn on" seçeneği ile inline modu etkinleştirin (isteğe bağlı)
8. "Edit Bot" > "Allow Groups" > "Turn on" seçeneği ile grup erişimini etkinleştirin

## 📦 Proje Yapısı

```
flirt-bot/
├── src/
│   ├── api/              # Backend API istekleri
│   │   └── task_api.py   # Görev API endpoints
│   ├── core/             # Ana bot işlevleri
│   │   └── bot_commands.py  # Komut işleyicileri
│   ├── tasks/            # Görev işleyicileri
│   │   ├── plugins/      # Görev eklentileri
│   │   ├── task_types/   # Görev tipleri
│   │   ├── base_task.py  # Temel görev sınıfı
│   │   └── task_manager.py # Görev yöneticisi
│   └── utils/            # Yardımcı fonksiyonlar
│       ├── task_logger.py # Görev logları
│       ├── nft_utils.py  # NFT/rozet işlemleri
│       └── json_logger.py # JSON formatında loglama
├── bot_listener.py       # Ana bot betiği
├── pyproject.toml        # Poetry yapılandırması
├── Dockerfile            # Docker yapılandırması
└── session_generator.py  # Oturum oluşturucu
```

## 🔄 Görev Tipleri

Bot, aşağıdaki görev tiplerini destekler:

- `bot_mention`: Kullanıcının botu bir grupta etiketlemesi
- `channel_join`: Belirtilen kanala katılma
- `channel_join_v2`: Gelişmiş kanal katılım kontrolü
- `group_join`: Belirtilen gruba katılma
- `group_join_message`: Gruba katılma ve mesaj gönderme
- `forward_message`: Belirli bir mesajı yönlendirme
- `post_share`: İçeriği paylaşma
- `deeplink_track`: Özel link takibi
- `pin_check`: Mesaj sabitleme kontrolü
- `message`: Belirli bir mesajı gönderme
- `message_send`: Bir gruba mesaj gönderme
- `emoji_reaction`: Mesaja emoji tepkisi verme
- `button_click`: Inline butonlara tıklama
- `referral`: Yeni kullanıcı davet etme
- `invite_tracker`: Gruba davet etme
- `share_count`: Paylaşım sayısı takibi
- `schedule_post`: Zamanlanmış mesaj gönderme
- `start_link`: Start link ile görev tamamlama

## 🤖 Komutlar

Bot aşağıdaki komutları destekler:

- `/start`: Bot'u başlatır ve karşılama mesajı gönderir
- `/tasks`: Mevcut görevleri liste halinde gösterir
- `/myprogress`: Kullanıcının görev ilerlemesini ve seviyesini gösterir
- `/gorev`: Yeni bir görev atar
- `/gorevlerim`: Kullanıcının tüm görevlerini listeler
- `/gunluk`: Günlük görev atar
- `/miniapp`: MiniApp'i açar
- `/help` ve `/yardim`: Yardım mesajı gösterir
- `/profil`: Kullanıcı profilini gösterir
- `/rozet`: Kazanılan rozetleri gösterir
- `/flirt`: Flört ipuçları verir
- `/agent`: Yapay zeka flört asistanı ile konuşma
- `/flortcoach`: Flört koçundan tavsiye alma
- `/tamamla`: Manuel görev tamamlama

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
